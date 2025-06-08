import os
import shutil
import sys
from textnode import TextNode, TextType, markdown_to_html_node, extract_title

def copy_files_recursive(source_dir, dest_dir):
    """
    Recursively copy all files and directories from source_dir to dest_dir.
    First deletes all contents of dest_dir if it exists.
    """
    # Delete destination directory if it exists
    if os.path.exists(dest_dir):
        print(f"Deleting existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create destination directory
    print(f"Creating directory: {dest_dir}")
    os.mkdir(dest_dir)
    
    # Copy all contents recursively
    _copy_directory_contents(source_dir, dest_dir)

def _copy_directory_contents(source_dir, dest_dir):
    """
    Helper function to recursively copy directory contents.
    """
    if not os.path.exists(source_dir):
        print(f"Source directory does not exist: {source_dir}")
        return
    
    # List all items in source directory
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isfile(source_path):
            # Copy file
            print(f"Copying file: {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            # Create directory and copy contents recursively
            print(f"Creating directory: {dest_path}")
            os.mkdir(dest_path)
            _copy_directory_contents(source_path, dest_path)

def generate_page(from_path, template_path, dest_path, basepath="/"):
    """
    Generate an HTML page from markdown content using a template.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    full_html = template_content.replace("{{ Title }}", title)
    full_html = full_html.replace("{{ Content }}", html_content)
    
    # Replace basepath references
    full_html = full_html.replace('href="/', f'href="{basepath}')
    full_html = full_html.replace('src="/', f'src="{basepath}')
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write HTML file
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """
    Recursively generate HTML pages for all markdown files in a directory.
    """
    if not os.path.exists(dir_path_content):
        print(f"Content directory does not exist: {dir_path_content}")
        return
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir_path):
        os.makedirs(dest_dir_path)
    
    # Process all items in the content directory
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        
        if os.path.isfile(item_path):
            # Check if it's a markdown file
            if item.endswith('.md'):
                # Generate corresponding HTML filename
                html_filename = item[:-3] + '.html'  # Replace .md with .html
                dest_path = os.path.join(dest_dir_path, html_filename)
                
                # Generate the page
                generate_page(item_path, template_path, dest_path, basepath)
                
        elif os.path.isdir(item_path):
            # Recursively process subdirectory
            subdest_path = os.path.join(dest_dir_path, item)
            generate_pages_recursive(item_path, template_path, subdest_path, basepath)

def main():
    # Get basepath from CLI argument, default to "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    
    print(f"Using basepath: {basepath}")
    
    # Copy static files to docs directory
    static_dir = "./static"
    docs_dir = "./docs"
    
    print("Starting file copy process...")
    copy_files_recursive(static_dir, docs_dir)
    print("File copy process completed!")
    
    # Generate all pages recursively
    print("\nGenerating pages...")
    generate_pages_recursive(
        "content",
        "template.html", 
        "docs",
        basepath
    )
    print("Page generation completed!")

if __name__ == "__main__":
    main()