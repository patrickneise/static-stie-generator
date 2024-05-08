from enum import StrEnum
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_FILE = os.path.join(BASE_DIR, "template.html")


class TextType(StrEnum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED = "unordered_list"
    ORDERED = "ordered_list"
