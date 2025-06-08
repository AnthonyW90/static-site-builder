import unittest
from textnode import TextNode, TextType, BlockType, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

        node3 = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertNotEqual(node, node3)

        node4 = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertEqual(node3, node4)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        node = TextNode("Code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "Code text")

    def test_link(self):
        node = TextNode("Link text", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Link text")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    # def test_image(self):
    #     node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.jpg")
    #     html_node = text_node_to_html_node(node)
    #     self.assertEqual(html_node.tag, "img")
    #     self.assertEqual(html_node.value, "")
    #     self.assertEqual(html_node.props, {"src": "https://example.com/image.jpg", "alt": "Alt text"})

    def test_unsupported_type(self):
        # Create a mock unsupported text type
        class UnsupportedType:
            pass
        
        node = TextNode("Test", UnsupportedType())
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_split_nodes_delimiter_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is text with a **bold phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold phrase", TextType.BOLD),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is text with an *italic phrase* here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("italic phrase", TextType.ITALIC),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_multiple_delimiters(self):
        node = TextNode("Here is `code` and **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_at_start(self):
        node = TextNode("**Bold** at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" at the start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_at_end(self):
        node = TextNode("Text ending with **bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_only_delimiter(self):
        node = TextNode("**just bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [TextNode("just bold", TextType.BOLD)]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_unmatched(self):
        node = TextNode("This has an unmatched `delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_split_nodes_delimiter_non_text_nodes(self):
        nodes = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("More `code` here", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("More ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_empty_delimiter_content(self):
        node = TextNode("Text with `` empty code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("", TextType.CODE),
            TextNode(" empty code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_images_no_images(self):
        text = "This is just regular text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_images_empty_alt(self):
        text = "Image with empty alt: ![](https://example.com/image.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "https://example.com/image.png")], matches)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_links_single(self):
        text = "Here is a [link](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_markdown_links_no_links(self):
        text = "This is just regular text with no links"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_empty_text(self):
        text = "Link with empty text: [](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("", "https://example.com")], matches)

    def test_extract_markdown_links_ignore_images(self):
        text = "This has an ![image](https://example.com/img.png) and a [link](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_markdown_images_mixed_with_links(self):
        text = "This has a [link](https://example.com) and an ![image](https://example.com/img.png)"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("image", "https://example.com/img.png")], image_matches)
        self.assertListEqual([("link", "https://example.com")], link_matches)

    def test_extract_markdown_complex_urls(self):
        text = "Complex URL [test](https://example.com/path?param=value&other=123#anchor)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("test", "https://example.com/path?param=value&other=123#anchor")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_single(self):
        node = TextNode("Text with ![single image](https://example.com/img.png) here", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("single image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_no_images(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_at_start(self):
        node = TextNode("![first image](https://example.com/img.png) at start", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("first image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_at_end(self):
        node = TextNode("Text ending with ![last image](https://example.com/img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("last image", TextType.IMAGE, "https://example.com/img.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_only_image(self):
        node = TextNode("![only image](https://example.com/img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("only image", TextType.IMAGE, "https://example.com/img.png")]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_non_text_nodes(self):
        nodes = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Text with ![image](https://example.com/img.png) here", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_single(self):
        node = TextNode("Text with [single link](https://example.com) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("single link", TextType.LINK, "https://example.com"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_no_links(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_at_start(self):
        node = TextNode("[first link](https://example.com) at start", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("first link", TextType.LINK, "https://example.com"),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_at_end(self):
        node = TextNode("Text ending with [last link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("last link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_only_link(self):
        node = TextNode("[only link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("only link", TextType.LINK, "https://example.com")]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_non_text_nodes(self):
        nodes = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Text with [link](https://example.com) here", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("Regular text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
            TextNode("Text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_ignore_images(self):
        node = TextNode("This has ![image](https://example.com/img.png) and [link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This has ![image](https://example.com/img.png) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_ignore_links(self):
        node = TextNode("This has [link](https://example.com) and ![image](https://example.com/img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This has [link](https://example.com) and ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_bold(self):
        text = "**bold text**"
        nodes = text_to_textnodes(text)
        expected = [TextNode("bold text", TextType.BOLD)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_italic(self):
        text = "*italic text*"
        nodes = text_to_textnodes(text)
        expected = [TextNode("italic text", TextType.ITALIC)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_code(self):
        text = "`code text`"
        nodes = text_to_textnodes(text)
        expected = [TextNode("code text", TextType.CODE)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_image(self):
        text = "![alt text](https://example.com/image.png)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("alt text", TextType.IMAGE, "https://example.com/image.png")]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_link(self):
        text = "[link text](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("link text", TextType.LINK, "https://example.com")]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_mixed_formatting(self):
        text = "Start **bold** and *italic* and `code` end"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_same_type(self):
        text = "**first bold** text **second bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("first bold", TextType.BOLD),
            TextNode(" text ", TextType.TEXT),
            TextNode("second bold", TextType.BOLD),
        ]
        self.assertListEqual(expected, nodes)

    # def test_text_to_textnodes_empty_string(self):
    #     text = ""
    #     nodes = text_to_textnodes(text)
    #     expected = [TextNode("", TextType.TEXT)]
    #     self.assertListEqual(expected, nodes)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "This is just a single paragraph with no double newlines"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is just a single paragraph with no double newlines"])

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_whitespace_only(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_excessive_newlines(self):
        md = """

First block


Second block



Third block

"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block", "Third block"])

    def test_markdown_to_blocks_with_whitespace(self):
        md = """  
  First block with leading spaces  

   Second block with spaces   

  Third block  
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block with leading spaces", "Second block with spaces", "Third block"])

    def test_markdown_to_blocks_complex_content(self):
        md = """# Heading 1

This is a paragraph with **bold** text.

## Heading 2

- List item 1
- List item 2
- List item 3

Another paragraph here.

```
code block
```"""
        blocks = markdown_to_blocks(md)
        expected = [
            "# Heading 1",
            "This is a paragraph with **bold** text.",
            "## Heading 2", 
            "- List item 1\n- List item 2\n- List item 3",
            "Another paragraph here.",
            "```\ncode block\n```"
        ]
        self.assertEqual(blocks, expected)

    def test_block_to_block_type_paragraph(self):
        block = "This is just a regular paragraph of text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_h2(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_h6(self):
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_invalid_no_space(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_invalid_too_many_hashes(self):
        block = "####### This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_code_block(self):
        block = "```\ncode here\nmore code\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_invalid(self):
        block = "```\ncode here\nmore code"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_multi_line(self):
        block = "> This is a quote\n> with multiple lines\n> of quoted text"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_invalid_missing_space(self):
        block = ">This is not a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_invalid_mixed(self):
        block = "> This is a quote\nThis is not"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_with_empty_lines(self):
        block = "> This is a quote\n>\n> with empty lines"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list_single_item(self):
        block = "- List item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_multiple_items(self):
        block = "- First item\n- Second item\n- Third item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_invalid_no_space(self):
        block = "-List item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_invalid_mixed(self):
        block = "- List item\nNot a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_single_item(self):
        block = "1. First item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_multiple_items(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_invalid_wrong_number(self):
        block = "1. First item\n3. Wrong number"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_invalid_no_space(self):
        block = "1.First item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_invalid_starts_wrong(self):
        block = "2. Starts with 2\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_invalid_mixed(self):
        block = "1. First item\nNot a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_with_formatting(self):
        block = "This is a paragraph with **bold** and *italic* text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_multiline(self):
        block = "This is a paragraph\nwith multiple lines\nbut no special formatting"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = """
# This is an h1

## This is an h2

### This is an h3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is an h1</h1><h2>This is an h2</h2><h3>This is an h3</h3></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> with multiple lines
> of quoted text
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote\nwith multiple lines\nof quoted text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- First item
- Second item
- Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. First item
2. Second item
3. Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item</li><li>Second item</li><li>Third item</li></ol></div>",
        )

#     def test_complex_markdown(self):
#         md = """
# # My Document

# This is a paragraph with **bold** text and a [link](https://example.com).

# ## Code Example

# ```
# def hello():
#     print("Hello, World!")
# ```

# > This is a quote with *italic* text.

# ### Lists

# #### Unordered:
# - Item one
# - Item two with `code`

# #### Ordered:
# 1. First
# 2. Second
# """
#         node = markdown_to_html_node(md)
#         html = node.to_html()
#         expected = "<div><h1>My Document</h1><p>This is a paragraph with <b>bold</b> text and a <a href=\"https://example.com\">link</a>.</p><h2>Code Example</h2><pre><code>def hello():\n    print(\"Hello, World!\")\n</code></pre><blockquote>This is a quote with <i>italic</i> text.</blockquote><h3>Lists</h3><h4>Unordered:</h4><ul><li>Item one</li><li>Item two with <code>code</code></li></ul><h4>Ordered:</h4><ol><li>First</li><li>Second</li></ol></div>"
#         self.assertEqual(html, expected)

    def test_inline_elements(self):
        md = """
This paragraph has **bold**, *italic*, `code`, ![image](https://example.com/img.png), and [link](https://example.com) elements.
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This paragraph has <b>bold</b>, <i>italic</i>, <code>code</code>, <img src=\"https://example.com/img.png\" alt=\"image\">, and <a href=\"https://example.com\">link</a> elements.</p></div>",
        )

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_heading_with_inline(self):
        md = "## Heading with **bold** text"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>Heading with <b>bold</b> text</h2></div>")

    def test_quote_with_inline(self):
        md = "> Quote with *italic* and `code` text"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>Quote with <i>italic</i> and <code>code</code> text</blockquote></div>")

    def test_quote_with_empty_lines(self):
        md = """> "I am in fact a Hobbit in all but size."
>
> -- J.R.R. Tolkien"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><blockquote>"I am in fact a Hobbit in all but size."\n\n-- J.R.R. Tolkien</blockquote></div>')

    def test_extract_title_simple(self):
        md = "# Hello"
        title = extract_title(md)
        self.assertEqual(title, "Hello")

    def test_extract_title_with_whitespace(self):
        md = "#   Hello World   "
        title = extract_title(md)
        self.assertEqual(title, "Hello World")

    def test_extract_title_with_content(self):
        md = """
# My Title

This is some content below the title.

## Another heading
"""
        title = extract_title(md)
        self.assertEqual(title, "My Title")

    def test_extract_title_no_h1(self):
        md = """
## This is an h2

This is some content.

### This is an h3
"""
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_extract_title_empty_markdown(self):
        md = ""
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_extract_title_only_h2_h3(self):
        md = """
## Heading 2

### Heading 3

Content here.
"""
        with self.assertRaises(ValueError):
            extract_title(md)


if __name__ == "__main__":
    unittest.main()