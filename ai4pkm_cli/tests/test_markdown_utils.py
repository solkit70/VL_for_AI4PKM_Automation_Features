"""
Unit tests for markdown_utils module.
"""
import pytest
from pathlib import Path
from ai4pkm_cli.markdown_utils import (
    extract_frontmatter,
    read_frontmatter,
    update_frontmatter_field,
    update_frontmatter_fields,
    extract_body
)


def test_extract_frontmatter_basic():
    """Test basic frontmatter extraction."""
    content = """---
title: Test Document
status: pending
count: 42
---

# Content
Test content here.
"""

    frontmatter = extract_frontmatter(content)

    assert frontmatter['title'] == 'Test Document'
    assert frontmatter['status'] == 'pending'
    assert frontmatter['count'] == 42  # yaml.safe_load parses numbers as int


def test_extract_frontmatter_with_quotes():
    """Test frontmatter with quoted values."""
    content = """---
title: "Quoted Title"
path: 'single quoted'
empty: ""
---

# Content
"""

    frontmatter = extract_frontmatter(content)

    assert frontmatter['title'] == 'Quoted Title'
    assert frontmatter['path'] == 'single quoted'
    assert frontmatter['empty'] == ''


def test_extract_frontmatter_with_booleans():
    """Test frontmatter with boolean values."""
    content = """---
enabled: true
disabled: false
---

# Content
"""

    frontmatter = extract_frontmatter(content)

    assert frontmatter['enabled'] is True
    assert frontmatter['disabled'] is False


def test_extract_frontmatter_empty():
    """Test frontmatter extraction when none exists."""
    content = """# Just Content

No frontmatter here.
"""

    frontmatter = extract_frontmatter(content)

    assert frontmatter == {}


def test_extract_frontmatter_with_comments():
    """Test frontmatter with comment lines."""
    content = """---
# This is a comment
title: Test
# Another comment
status: pending
---

# Content
"""

    frontmatter = extract_frontmatter(content)

    assert frontmatter['title'] == 'Test'
    assert frontmatter['status'] == 'pending'
    assert '#' not in frontmatter


def test_read_frontmatter(tmp_path):
    """Test reading frontmatter from file."""
    test_file = tmp_path / "test.md"
    test_file.write_text("""---
title: File Test
created: "2025-10-25"
---

# Content
Test content.
""", encoding='utf-8')

    frontmatter = read_frontmatter(test_file)

    assert frontmatter['title'] == 'File Test'
    assert frontmatter['created'] == '2025-10-25'  # Quoted to keep as string


def test_read_frontmatter_nonexistent_file(tmp_path):
    """Test reading frontmatter from nonexistent file."""
    test_file = tmp_path / "nonexistent.md"

    frontmatter = read_frontmatter(test_file)

    assert frontmatter == {}


def test_update_frontmatter_field_existing():
    """Test updating an existing frontmatter field."""
    content = """---
title: Original
status: pending
---

# Content
Body text.
"""

    updated = update_frontmatter_field(content, 'status', 'completed')

    assert 'status: "completed"' in updated
    assert 'status: pending' not in updated
    assert '# Content' in updated
    assert 'Body text.' in updated


def test_update_frontmatter_field_new():
    """Test adding a new frontmatter field."""
    content = """---
title: Test
---

# Content
Body text.
"""

    updated = update_frontmatter_field(content, 'status', 'new_value')

    assert 'status: "new_value"' in updated
    assert 'title: Test' in updated
    assert '# Content' in updated


def test_update_frontmatter_field_no_frontmatter():
    """Test updating field when no frontmatter exists."""
    content = """# Just Content

No frontmatter here.
"""

    updated = update_frontmatter_field(content, 'status', 'value')

    # Should return content unchanged
    assert updated == content


def test_update_frontmatter_fields_multiple():
    """Test updating multiple frontmatter fields at once."""
    content = """---
title: Original
status: pending
---

# Content
"""

    updates = {
        'status': 'completed',
        'worker': 'EIC',
        'count': '5'
    }

    updated = update_frontmatter_fields(content, updates)

    assert 'status: "completed"' in updated
    assert 'worker: "EIC"' in updated
    assert 'count: "5"' in updated


def test_extract_body():
    """Test extracting body content."""
    content = """---
title: Test
status: pending
---

# Main Content

This is the body.
"""

    body = extract_body(content)

    assert '# Main Content' in body
    assert 'This is the body.' in body
    assert 'title: Test' not in body
    assert '---' not in body


def test_extract_body_no_frontmatter():
    """Test extracting body when no frontmatter exists."""
    content = """# Just Content

No frontmatter here.
"""

    body = extract_body(content)

    assert body == content
