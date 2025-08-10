"""
XML formatters for ByGoD.

This module contains functions for formatting Bible data into XML format
with metadata and structured hierarchy.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.translations import BIBLE_TRANSLATIONS


def format_as_xml(data: List[Dict[str, Any]], translation: str = "NIV") -> str:
    """
    Format Bible data as XML with metadata.

    Args:
        data: List of Bible passage dictionaries
        translation: Bible translation code (e.g., "NIV")

    Returns:
        Formatted XML string
    """
    if not data:
        return '<?xml version="1.0" encoding="UTF-8"?>\n<bible error="No data to format" />'

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Create XML structure
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append("<bible>")

    # Add metadata
    xml_parts.append("  <metadata>")
    xml_parts.append(f'    <translation code="{translation}">')
    xml_parts.append(f'      <name>{translation_info["name"]}</name>')
    xml_parts.append(f'      <language>{translation_info["language"]}</language>')
    xml_parts.append("    </translation>")
    xml_parts.append(
        f"    <generated>{datetime.now(timezone.utc).isoformat()}</generated>"
    )
    xml_parts.append(f"    <total_passages>{len(data)}</total_passages>")
    xml_parts.append("    <format>xml</format>")
    xml_parts.append("  </metadata>")

    # Group data by book
    books = {}
    for passage in data:
        book = passage.get("book", "Unknown")
        if book not in books:
            books[book] = []
        books[book].append(passage)

    # Add books
    xml_parts.append("  <books>")
    for book_name, passages in books.items():
        xml_parts.append(f'    <book name="{book_name}">')
        for passage in passages:
            xml_parts.append("      <passage>")
            xml_parts.append(f'        <chapter>{passage.get("chapter", "")}</chapter>')
            xml_parts.append(f'        <verse>{passage.get("verse", "")}</verse>')
            xml_parts.append(f'        <text>{passage.get("text", "")}</text>')
            xml_parts.append("      </passage>")
        xml_parts.append("    </book>")
    xml_parts.append("  </books>")

    xml_parts.append("</bible>")

    return "\n".join(xml_parts)


def format_master_xml(all_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format multiple translations as a single XML file.

    Args:
        all_data: Dictionary with translation codes as keys and Bible data as values

    Returns:
        Formatted XML string
    """
    if not all_data:
        return '<?xml version="1.0" encoding="UTF-8"?>\n<bible error="No data to format" />'

    # Create XML structure
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append("<bible>")

    # Add metadata
    xml_parts.append("  <metadata>")
    xml_parts.append(
        f"    <generated>{datetime.now(timezone.utc).isoformat()}</generated>"
    )
    xml_parts.append(f"    <total_translations>{len(all_data)}</total_translations>")
    xml_parts.append("    <format>xml</format>")
    xml_parts.append("    <translations>")

    for translation, data in all_data.items():
        translation_info = BIBLE_TRANSLATIONS.get(
            translation, {"name": translation, "language": "Unknown"}
        )
        xml_parts.append(f'      <translation code="{translation}">')
        xml_parts.append(f'        <name>{translation_info["name"]}</name>')
        xml_parts.append(f'        <language>{translation_info["language"]}</language>')
        xml_parts.append(f"        <total_passages>{len(data)}</total_passages>")
        xml_parts.append("      </translation>")

    xml_parts.append("    </translations>")
    xml_parts.append("  </metadata>")

    # Add translations
    xml_parts.append("  <translations>")
    for translation, data in all_data.items():
        xml_parts.append(f'    <translation code="{translation}">')

        # Group data by book
        books = {}
        for passage in data:
            book = passage.get("book", "Unknown")
            if book not in books:
                books[book] = []
            books[book].append(passage)

        # Add books
        for book_name, passages in books.items():
            xml_parts.append(f'      <book name="{book_name}">')
            for passage in passages:
                xml_parts.append("        <passage>")
                xml_parts.append(
                    f'          <chapter>{passage.get("chapter", "")}</chapter>'
                )
                xml_parts.append(f'          <verse>{passage.get("verse", "")}</verse>')
                xml_parts.append(f'          <text>{passage.get("text", "")}</text>')
                xml_parts.append("        </passage>")
            xml_parts.append("      </book>")

        xml_parts.append("    </translation>")
    xml_parts.append("  </translations>")

    xml_parts.append("</bible>")

    return "\n".join(xml_parts)
