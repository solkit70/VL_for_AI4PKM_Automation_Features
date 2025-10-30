"""
Utilities for reading and writing markdown file frontmatter.

This module provides functions to parse and update YAML frontmatter
in markdown files. Used by both KTM (legacy) and orchestrator (new).
"""
import re
import yaml
from typing import Dict, Any
from pathlib import Path


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Dictionary of frontmatter properties
    """
    # Match YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    yaml_content = match.group(1)

    try:
        # Use yaml.safe_load for proper YAML parsing (handles lists, nested structures, etc.)
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter if frontmatter is not None else {}
    except yaml.YAMLError:
        # Fall back to empty dict if YAML is invalid
        return {}


def read_frontmatter(file_path: Path) -> Dict[str, Any]:
    """
    Read and parse frontmatter from markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary of frontmatter properties
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        return extract_frontmatter(content)
    except Exception:
        return {}


def update_frontmatter_field(content: str, field: str, value: str) -> str:
    """
    Update a field in YAML frontmatter.

    Args:
        content: Full markdown content
        field: Field name to update
        value: New value

    Returns:
        Updated content
    """
    # Match frontmatter
    match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
    if not match:
        return content

    prefix = match.group(1)
    yaml_content = match.group(2)
    suffix = match.group(3)
    rest = content[match.end():]

    # Check if field exists
    field_pattern = rf'^{field}:\s*.*$'
    if re.search(field_pattern, yaml_content, re.MULTILINE):
        # Update existing field
        yaml_content = re.sub(field_pattern, f'{field}: "{value}"', yaml_content, flags=re.MULTILINE)
    else:
        # Add new field
        yaml_content += f'\n{field}: "{value}"'

    return prefix + yaml_content + suffix + rest


def update_frontmatter_fields(content: str, updates: Dict[str, str]) -> str:
    """
    Update multiple fields in YAML frontmatter.

    Args:
        content: Full markdown content
        updates: Dictionary of field: value pairs to update

    Returns:
        Updated content
    """
    for field, value in updates.items():
        content = update_frontmatter_field(content, field, value)
    return content


def extract_body(content: str) -> str:
    """
    Extract body content (after frontmatter) from markdown.

    Args:
        content: Full markdown content

    Returns:
        Body content (everything after frontmatter)
    """
    # Remove frontmatter
    match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def remove_pattern_from_content(content: str, pattern: str) -> str:
    """
    Remove pattern from content using regex.

    Generic utility for removing patterns from markdown content.
    Used for post-processing after agent execution.

    Args:
        content: Full markdown content
        pattern: Regex pattern to remove

    Returns:
        Content with pattern removed
    """
    try:
        # Remove pattern (case-insensitive, multiline)
        updated = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        return updated
    except re.error as e:
        # If pattern is invalid, return content unchanged
        return content
