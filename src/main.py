import generate


def main():
    markdown = """
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items

# This is Heading 1

* mess up
- ordered list

## This is a Heading 2

```
This is a code block
with multiple lines
```

### This is Heading 3

1. Ordered **bold**
2. List

> This is
> a quote

> this is a messed
up quote
    """

    html_nodes = generate.markdown_to_html_node(markdown)
    print("\n\n", html_nodes.to_html())


main()
