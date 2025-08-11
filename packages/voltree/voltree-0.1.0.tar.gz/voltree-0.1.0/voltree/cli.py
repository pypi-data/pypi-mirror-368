# voltree/cli.py

import os
import argparse
import sys
from colorama import init, Fore, Style

# Enable color support for Windows and Unix terminals
init(autoreset=True)

class Node:
    """
    Represents a folder or file in the structure tree.
    """
    def __init__(self, name, is_file=False):
        self.name = name
        self.is_file = is_file
        self.children = []

    def add_child(self, child):
        self.children.append(child)

def generate_template(ext, filename):
    """
    Return a default template content for known file extensions.
    """
    templates = {
        '.py': f"# {filename} - Python file\n\n",
        '.md': f"# {filename}\n\n",
        '.txt': "",
        '.json': "{}\n",
        '.sh': "#!/bin/bash\n\n",
        '.html': "<!-- HTML file -->\n",
        '.js': f"// {filename} - JavaScript file\n\n",
        '.css': "/* CSS file */\n",
        '.yml': "# YAML config\n",
        '.yaml': "# YAML config\n",
    }
    return templates.get(ext.lower(), "")

def build_trees(tokens_list):
    """
    Build one or more tree structures from tokenized input lines.
    """
    roots = []
    for tokens in tokens_list:
        root = None
        current_nodes = []

        for token in tokens:
            if token.startswith('--'):
                # Multiple files inside current folder
                files = token.split('--')[1:]
                for f in files:
                    if not f.strip():
                        raise ValueError("File name cannot be empty.")
                    if not current_nodes:
                        raise ValueError(f"File '{f}' must be inside a folder.")
                    current_nodes[-1].add_child(Node(f, is_file=True))

            elif token.startswith('-'):
                # Subfolder
                folder = token[1:]
                if not folder.strip():
                    raise ValueError("Folder name cannot be empty.")
                new_node = Node(folder)
                if current_nodes:
                    current_nodes[-1].add_child(new_node)
                else:
                    root = new_node
                current_nodes.append(new_node)

            else:
                # Top-level folder
                folder = token
                if not folder.strip():
                    raise ValueError("Folder name cannot be empty.")
                new_node = Node(folder)
                if current_nodes:
                    current_nodes[-1].add_child(new_node)
                else:
                    root = new_node
                current_nodes.append(new_node)

        if root is None:
            raise ValueError("No root folder found in input.")
        roots.append(root)
    return roots

def parse_structure(input_str):
    """
    Parses the full multiline structure definition into token lists.
    """
    lines = [line.strip() for line in input_str.strip().splitlines() if line.strip()]
    tokens_list = [line.split('/') for line in lines]
    return build_trees(tokens_list)

def print_tree(node, prefix='', is_last=True, ancestors_has_next=[]):
    """
    Recursively print a colorized tree structure.
    """
    connector = '└── ' if is_last else '├── '
    color = Fore.GREEN if node.is_file else Fore.CYAN
    print(prefix + connector + color + node.name + Style.RESET_ALL)

    if node.children:
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix
            for has_next in ancestors_has_next:
                new_prefix += '│   ' if has_next else '    '
            new_prefix += '    ' if is_last else '│   '
            print_tree(child, new_prefix, is_last_child, ancestors_has_next + [not is_last])

def create_files_and_dirs(node, base_path=''):
    """
    Create the actual folders and files based on the Node tree.
    """
    path = os.path.join(base_path, node.name)
    if node.is_file:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            ext = os.path.splitext(node.name)[1]
            content = generate_template(ext, node.name)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    else:
        os.makedirs(path, exist_ok=True)
        for child in node.children:
            create_files_and_dirs(child, path)

def main():
    parser = argparse.ArgumentParser(
        description="🌳 Voltree - Instantly create folder/file structures using a simple string format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Structure Syntax:
  /         → separates levels (folders/files)
  -folder   → subfolder inside the previous folder
  --file    → file(s) in the current folder

Examples:
  voltree "Project/-src/--main.py--utils.py/-docs/--README.md"
  voltree --dry-run "MyApp/-core/--index.js--helpers.js"

Multiple Roots:
  voltree "App/-src/--main.py" "Docs/--README.md"

From File:
  voltree -f structure.txt
"""
    )
    parser.add_argument('structure', nargs='*', help='Structure string or multiple root definitions')
    parser.add_argument('-f', '--file', help='Read structure from a text file')
    parser.add_argument('--dry-run', action='store_true', help='Only display the tree structure without creating files')
    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                structure = f.read().strip()
            if not structure:
                print("❌ The input file is empty.")
                sys.exit(1)
        elif args.structure:
            structure = "\n".join(args.structure)
        else:
            parser.print_help()
            sys.exit(0)

        roots = parse_structure(structure)

        if args.dry_run:
            print()
            for i, root in enumerate(roots):
                print(Fore.CYAN + root.name + Style.RESET_ALL)
                for j, child in enumerate(root.children):
                    print_tree(child, '', j == len(root.children) - 1, [])
                if i != len(roots) - 1:
                    print()
            print("\n✅ Dry run completed. No files or folders were created.")
        else:
            for root in roots:
                create_files_and_dirs(root)
            print("\n✅ Project structure created successfully.")

    except Exception as e:
        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == '__main__':
    main()
