"""
YAML formatters for ByGoD.

This module contains functions for formatting Bible data into YAML format
with metadata and structured hierarchy.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.translations import BIBLE_TRANSLATIONS


def format_as_yaml(data: List[Dict[str, Any]], translation: str = "NIV") -> str:
    """
    Format Bible data as YAML with metadata.

    Args:
        data: List of Bible passage dictionaries
        translation: Bible translation code (e.g., "NIV")

    Returns:
        Formatted YAML string
    """
    if not data:
        return "error: No data to format\n"

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Create YAML structure
    yaml_parts = []

    # Add metadata
    yaml_parts.append("metadata:")
    yaml_parts.append(f"  translation:")
    yaml_parts.append(f"    code: {translation}")
    yaml_parts.append(f"    name: {translation_info['name']}")
    yaml_parts.append(f"    language: {translation_info['language']}")
    yaml_parts.append(f"  generated: {datetime.now(timezone.utc).isoformat()}")
    yaml_parts.append(f"  total_passages: {len(data)}")
    yaml_parts.append("  format: yaml")

    # Group data by book
    books = {}
    for passage in data:
        book = passage.get("book", "Unknown")
        if book not in books:
            books[book] = []
        books[book].append(passage)

    # Add books
    yaml_parts.append("books:")
    for book_name, passages in books.items():
        yaml_parts.append(f"  {book_name}:")
        for passage in passages:
            yaml_parts.append("    - passage:")
            yaml_parts.append(f"        chapter: {passage.get('chapter', '')}")
            yaml_parts.append(f"        verse: {passage.get('verse', '')}")
            yaml_parts.append(f"        text: {passage.get('text', '')}")

    return "\n".join(yaml_parts)


def format_master_yaml(all_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format multiple translations as a single YAML file.

    Args:
        all_data: Dictionary with translation codes as keys and Bible data as values

    Returns:
        Formatted YAML string
    """
    if not all_data:
        return "error: No data to format\n"

    # Create YAML structure
    yaml_parts = []

    # Add metadata
    yaml_parts.append("metadata:")
    yaml_parts.append(f"  generated: {datetime.now(timezone.utc).isoformat()}")
    yaml_parts.append(f"  total_translations: {len(all_data)}")
    yaml_parts.append("  format: yaml")
    yaml_parts.append("  translations:")

    for translation, data in all_data.items():
        translation_info = BIBLE_TRANSLATIONS.get(
            translation, {"name": translation, "language": "Unknown"}
        )
        yaml_parts.append(f"    {translation}:")
        yaml_parts.append(f"      name: {translation_info['name']}")
        yaml_parts.append(f"      language: {translation_info['language']}")
        yaml_parts.append(f"      total_passages: {len(data)}")

    # Add translations
    yaml_parts.append("translations:")
    for translation, data in all_data.items():
        yaml_parts.append(f"  {translation}:")

        # Group data by book
        books = {}
        for passage in data:
            book = passage.get("book", "Unknown")
            if book not in books:
                books[book] = []
            books[book].append(passage)

        # Add books
        for book_name, passages in books.items():
            yaml_parts.append(f"    {book_name}:")
            for passage in passages:
                yaml_parts.append("      - passage:")
                yaml_parts.append(f"          chapter: {passage.get('chapter', '')}")
                yaml_parts.append(f"          verse: {passage.get('verse', '')}")
                yaml_parts.append(f"          text: {passage.get('text', '')}")

    return "\n".join(yaml_parts)
