#!/usr/bin/env python3
"""
Generate README.md from template by injecting example code.

This script reads the README template and injects the explore_database.py
example code into the placeholder.
"""

import sys


def read_file(filepath):
    """Read file content safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f'Error: File {filepath} not found')
        return None
    except Exception as e:
        print(f'Error reading {filepath}: {e}')
        return None


def write_file(filepath, content):
    """Write file content safely."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f'Error writing {filepath}: {e}')
        return False


def strip_github_only_sections(content):
    """Strip GitHub-only sections from content."""
    import re

    # Remove content between <!-- GITHUB_ONLY_START --> and <!-- GITHUB_ONLY_END -->
    # Use DOTALL flag to match across newlines
    pattern = r'<!-- GITHUB_ONLY_START -->.*?<!-- GITHUB_ONLY_END -->'
    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Clean up any extra blank lines that might be left
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)

    return cleaned_content


def remove_github_only_markers(content):
    """Remove GitHub-only markers but keep the content."""
    import re

    # Remove the start marker
    content = re.sub(r'<!-- GITHUB_ONLY_START -->\s*\n?', '', content)

    # Remove the end marker
    content = re.sub(r'\s*<!-- GITHUB_ONLY_END -->\s*\n?', '', content)

    return content


def main():
    """Main function to generate README from template."""
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate README from template by injecting example code'
    )
    parser.add_argument(
        '--template',
        default='README.template.md',
        help='Path to the README template file (default: README.template.md)',
    )
    parser.add_argument(
        '--example',
        default='examples/explore_database.py',
        help='Path to the example file to inject (default: examples/explore_database.py)',
    )
    parser.add_argument(
        '--output', default='README.md', help='Path to the output README file (default: README.md)'
    )
    parser.add_argument(
        '--placeholder',
        default='<!-- EXPLORE_DATABASE_EXAMPLE_PLACEHOLDER -->',
        help='Placeholder text to replace in template '
        '(default: <!-- EXPLORE_DATABASE_EXAMPLE_PLACEHOLDER -->)',
    )
    parser.add_argument(
        '--strip-github-only',
        action='store_true',
        help='Strip GitHub-only sections '
        '(content between <!-- GITHUB_ONLY_START --> and <!-- GITHUB_ONLY_END -->)',
    )

    args = parser.parse_args()

    # Use provided arguments
    template_path = args.template
    example_path = args.example
    output_path = args.output
    placeholder = args.placeholder

    # Read the template
    template_content = read_file(template_path)
    if template_content is None:
        sys.exit(1)

    # Read the example file
    example_content = read_file(example_path)
    if example_content is None:
        print(f'Warning: {example_path} not found, using placeholder')
        example_content = '# Example file not found'

    # Replace placeholder with actual content
    updated_content = template_content.replace(placeholder, example_content)

    # Handle GitHub-only sections
    if args.strip_github_only:
        # Strip GitHub-only sections for PyPI
        updated_content = strip_github_only_sections(updated_content)
    else:
        # Remove markers but keep content for GitHub
        updated_content = remove_github_only_markers(updated_content)

    # Write the updated README
    if write_file(output_path, updated_content):
        print(f'Successfully generated {output_path} from {template_path}')
        print(f'Injected content from {example_path}')
        print(f'Replaced placeholder: {placeholder}')
        if args.strip_github_only:
            print('Stripped GitHub-only sections for PyPI release')
    else:
        print(f'Failed to write {output_path}')
        sys.exit(1)


if __name__ == '__main__':
    main()
