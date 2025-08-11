"""
XML formatter for Bible data.

This module contains functions for formatting Bible data into XML format
with metadata and structured organization.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.copyright import get_copyright_url
from ..constants.translations import BIBLE_TRANSLATIONS
from ..constants.version import VERSION


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def format_as_xml(data: List[Dict[str, Any]], translation: str) -> str:
    """
    Format Bible data as XML.

    Args:
        data: List of Bible passages
        translation: Translation abbreviation (e.g., 'ESV', 'NIV')

    Returns:
        Formatted XML string
    """
    if not data:
        return '<?xml version="1.0" encoding="utf-8"?>\n<root>\n  <error>No data to format</error>\n</root>'

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Get language abbreviation (first 2 letters of language name)
    language = translation_info["language"]
    language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

    # Create XML structure
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']
    xml_parts.append("<root>")

    # Add meta section
    xml_parts.append("  <meta>")
    xml_parts.append(f"    <language>{language}</language>")
    xml_parts.append(f"    <translation>{translation}</translation>")
    copyright_url = get_copyright_url(translation)
    xml_parts.append(f"    <copyright>{copyright_url}</copyright>")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    xml_parts.append(f"    <timestamp>{timestamp}</timestamp>")
    xml_parts.append(f"    <ByGod>{VERSION}</ByGod>")
    xml_parts.append("  </meta>")

    # Add main structure: language name="abbr" -> translation name="abbr" -> book -> chapter -> passage
    xml_parts.append(f'  <language name="{language_abbr}">')
    xml_parts.append(f'    <translation name="{translation}">')

    # Group data by book and chapter
    books_data = {}
    for passage in data:
        book = passage.get("book", "Unknown")
        chapter = passage.get("chapter", "1")
        verses = passage.get("verses", [])

        if book not in books_data:
            books_data[book] = {}

        if chapter not in books_data[book]:
            books_data[book][chapter] = []

        books_data[book][chapter].extend(verses)

    # Add books with proper structure
    for book_name, chapters in books_data.items():
        # Create book tag with name and tag attributes
        book_tag = re.sub(r"[^a-zA-Z0-9]", "_", book_name)
        xml_parts.append(f'      <book name="{book_name}" tag="_{book_tag}">')

        for chapter_num, verses in chapters.items():
            xml_parts.append(f'        <chapter number="{chapter_num}">')
            for i, verse_text in enumerate(verses):
                passage_num = i + 1
                escaped_text = escape_xml(verse_text)
                xml_parts.append(
                    f'          <passage number="{passage_num}">{escaped_text}</passage>'
                )
            xml_parts.append("        </chapter>")

        xml_parts.append("      </book>")

    xml_parts.append("    </translation>")
    xml_parts.append("  </language>")
    xml_parts.append("</root>")

    return "\n".join(xml_parts)


def format_master_xml(data: List[Dict[str, Any]], translation: str) -> str:
    """
    Format master Bible data as XML.

    Args:
        data: List of Bible passages
        translation: Translation abbreviation (e.g., 'ESV', 'NIV')

    Returns:
        Formatted XML string
    """
    if not data:
        return '<?xml version="1.0" encoding="utf-8"?>\n<root>\n  <error>No data to format</error>\n</root>'

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Get language abbreviation (first 2 letters of language name)
    language = translation_info["language"]
    language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

    # Create XML structure
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']
    xml_parts.append("<root>")

    # Add meta section
    xml_parts.append("  <meta>")
    xml_parts.append(f"    <language>{language}</language>")
    xml_parts.append(f"    <translation>{translation}</translation>")
    copyright_url = get_copyright_url(translation)
    xml_parts.append(f"    <copyright>{copyright_url}</copyright>")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    xml_parts.append(f"    <timestamp>{timestamp}</timestamp>")
    xml_parts.append(f"    <ByGod>{VERSION}</ByGod>")
    xml_parts.append("  </meta>")

    # Add main structure: language name="abbr" -> translation name="abbr" -> book -> chapter -> passage
    xml_parts.append(f'  <language name="{language_abbr}">')
    xml_parts.append(f'    <translation name="{translation}">')

    # Group data by book and chapter
    books_data = {}
    for passage in data:
        book = passage.get("book", "Unknown")
        chapter = passage.get("chapter", "1")
        verses = passage.get("verses", [])

        if book not in books_data:
            books_data[book] = {}

        if chapter not in books_data[book]:
            books_data[book][chapter] = []

        books_data[book][chapter].extend(verses)

    # Add books with proper structure
    for book_name, chapters in books_data.items():
        # Create book tag with name and tag attributes
        book_tag = re.sub(r"[^a-zA-Z0-9]", "_", book_name)
        xml_parts.append(f'      <book name="{book_name}" tag="_{book_tag}">')

        for chapter_num, verses in chapters.items():
            xml_parts.append(f'        <chapter number="{chapter_num}">')
            for i, verse_text in enumerate(verses):
                passage_num = i + 1
                escaped_text = escape_xml(verse_text)
                xml_parts.append(
                    f'          <passage number="{passage_num}">{escaped_text}</passage>'
                )
            xml_parts.append("        </chapter>")

        xml_parts.append("      </book>")

    xml_parts.append("    </translation>")
    xml_parts.append("  </language>")
    xml_parts.append("</root>")

    return "\n".join(xml_parts)
