from enum import Enum
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str|None = None):
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextNode):
            return False
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def text_node_to_html_node(text_node):
    from htmlnode import LeafNode
    
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        # Create a special image node that renders as self-closing
        return ImageNode(text_node.text, text_node.url)
    else:
        raise ValueError(f"Unsupported TextType: {text_node.text_type}")


class ImageNode:
    def __init__(self, alt_text, src):
        self.alt_text = alt_text
        self.src = src
    
    def to_html(self):
        return f'<img src="{self.src}" alt="{self.alt_text}">'


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        parts = node.text.split(delimiter)
        
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}'")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        text = node.text
        images = extract_markdown_images(text)
        
        if not images:
            new_nodes.append(node)
            continue
        
        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            parts = text.split(image_markdown, 1)
            
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            text = parts[1]
        
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        text = node.text
        links = extract_markdown_links(text)
        
        if not links:
            new_nodes.append(node)
            continue
        
        for link_text, url in links:
            link_markdown = f"[{link_text}]({url})"
            parts = text.split(link_markdown, 1)
            
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            
            text = parts[1]
        
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    
    for block in blocks:
        stripped_block = block.strip()
        if stripped_block:
            filtered_blocks.append(stripped_block)
    
    return filtered_blocks


def block_to_block_type(block):
    lines = block.split("\n")
    
    # Check for heading
    if block.startswith("#"):
        heading_match = re.match(r"^#{1,6} ", block)
        if heading_match:
            return BlockType.HEADING
    
    # Check for code block
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote block
    if all(line.startswith("> ") or line.strip() == ">" for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list
    if len(lines) > 0:
        is_ordered_list = True
        for i, line in enumerate(lines):
            expected_prefix = f"{i + 1}. "
            if not line.startswith(expected_prefix):
                is_ordered_list = False
                break
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    from htmlnode import LeafNode
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def markdown_to_html_node(markdown):
    from htmlnode import ParentNode, LeafNode
    
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            # Replace newlines with spaces in paragraphs
            paragraph_text = block.replace("\n", " ")
            children = text_to_children(paragraph_text)
            block_nodes.append(ParentNode("p", children))
            
        elif block_type == BlockType.HEADING:
            # Count the number of # characters
            level = 0
            for char in block:
                if char == "#":
                    level += 1
                else:
                    break
            heading_text = block[level + 1:]  # Skip the # and space
            children = text_to_children(heading_text)
            block_nodes.append(ParentNode(f"h{level}", children))
            
        elif block_type == BlockType.CODE:
            # Remove the ``` from start and end, and strip leading newline if present
            code_text = block[3:-3]
            if code_text.startswith("\n"):
                code_text = code_text[1:]
            code_node = LeafNode("code", code_text)
            block_nodes.append(ParentNode("pre", [code_node]))
            
        elif block_type == BlockType.QUOTE:
            # Remove "> " from each line, handle lines that are just ">"
            lines = block.split("\n")
            quote_lines = []
            for line in lines:
                if line.startswith("> "):
                    quote_lines.append(line[2:])
                elif line.strip() == ">":
                    quote_lines.append("")
                else:
                    quote_lines.append(line)
            quote_text = "\n".join(quote_lines)
            children = text_to_children(quote_text)
            block_nodes.append(ParentNode("blockquote", children))
            
        elif block_type == BlockType.UNORDERED_LIST:
            # Create list items
            lines = block.split("\n")
            list_items = []
            for line in lines:
                item_text = line[2:]  # Remove "- "
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            block_nodes.append(ParentNode("ul", list_items))
            
        elif block_type == BlockType.ORDERED_LIST:
            # Create list items
            lines = block.split("\n")
            list_items = []
            for line in lines:
                # Find the ". " and remove everything before it
                dot_index = line.find(". ")
                item_text = line[dot_index + 2:]
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            block_nodes.append(ParentNode("ol", list_items))
    
    return ParentNode("div", block_nodes)


def extract_title(markdown):
    lines = markdown.strip().split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('# ') and not stripped_line.startswith('## '):
            # Found h1 header, extract title
            title = stripped_line[2:].strip()
            return title
    
    raise ValueError("No h1 header found in markdown")