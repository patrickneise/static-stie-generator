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

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        return (
            "".join([f' {key}="{value}"' for key, value in self.props.items()])
            if self.props
            else ""
        )

    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"


class LeafNode(HTMLNode):
    def __init__(
        self, tag: str = None, value: str = None, props: Dict[str, str] = None
    ):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
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
            raise ValueError("Tag is required for parent node")
        if not self.children:
            raise ValueError("Children are required for parent node")

        inner_html = ""
        for node in self.children:
            inner_html += node.to_html()

        return f"<{self.tag}{self.props_to_html()}>{inner_html}</{self.tag}>"


def text_node_to_html_node(text_node: parse.TextNode):
    if text_node.text_type == "text":
        return LeafNode(None, text_node.text)
    elif text_node.text_type == "bold":
        return LeafNode("b", text_node.text)
    elif text_node.text_type == "italic":
        return LeafNode("i", text_node.text)
    elif text_node.text_type == "code":
        return LeafNode("code", text_node.text)
    elif text_node.text_type == "link":
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == "image":
        return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError("Unknown node type")


def quote_to_html(block):
    block_text = " ".join([line.lstrip("> ") for line in block.split("\n")])
    return LeafNode("blockquote", block_text)


def unordered_to_html(block):
    items = [
        LeafNode("li", parse.text_to_textnodes(line.lstrip("*- ")))
        for line in block.split("\n")
    ]
    return ParentNode("ul", items)


def ordered_to_html(block):
    items = [
        LeafNode("li", parse.text_to_textnodes(line.split(" ")[1]))
        for line in block.split("\n")
    ]
    return ParentNode("ol", items)


def code_to_html(block):
    code = LeafNode("pre", "\n".join(block.split("\n")[1:-1]))
    return ParentNode("code", [code])


def heading_to_html(block):
    level = len(block.split(" ")[0])
    text = block.lstrip("# ")
    return LeafNode(f"h{level}", text)


def paragraph_to_html(block):
    paragraph = " ".join([line.strip() for line in block.split("\n")])
    return LeafNode("p", paragraph)


def markdown_to_html_node(markdown: str) -> ParentNode:
    nodes = []
    blocks = parse.markdown_to_blocks(markdown)
    for block in blocks:
        block_type = parse.block_to_block_type(block)
        if block_type == parse.Block.QUOTE.value:
            nodes.append(quote_to_html(block))
        if block_type == parse.Block.UNORDERED.value:
            nodes.append(unordered_to_html(block))
        if block_type == parse.Block.ORDERED.value:
            nodes.append(ordered_to_html(block))
        if block_type == parse.Block.CODE.value:
            nodes.append(code_to_html(block))
        if block_type == parse.Block.HEADING.value:
            nodes.append(heading_to_html(block))
        if block_type == parse.Block.PARAGRAPH.value:
            nodes.append(paragraph_to_html(block))
    return ParentNode("div", nodes)
