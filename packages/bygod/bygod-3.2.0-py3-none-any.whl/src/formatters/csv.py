"""
CSV formatter for Bible data.

This module contains functions for formatting Bible data into CSV format
with metadata and structured organization.
"""

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.copyright import get_copyright_url
from ..constants.translations import BIBLE_TRANSLATIONS
from ..constants.version import VERSION


def format_as_csv(data: List[Dict[str, Any]], translation: str) -> str:
    """
    Format Bible data as CSV.

    Args:
        data: List of Bible passages
        translation: Translation abbreviation (e.g., 'ESV', 'NIV')

    Returns:
        Formatted CSV string
    """
    if not data:
        return "Book,Chapter,Passage,Language,Translation,Copyright,Timestamp,ByGod\n"

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Get language abbreviation (first 2 letters of language name)
    language = translation_info["language"]
    language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

    # Create CSV structure
    output = io.StringIO()
    writer = csv.writer(output)

    # Add headers
    writer.writerow(
        [
            "Book",
            "Chapter",
            "Passage",
            "Language",
            "Translation",
            "Copyright",
            "Timestamp",
            "ByGod",
        ]
    )

    # Add data rows
    first_row = True
    for passage in data:
        book = passage.get("book", "Unknown")
        chapter = passage.get("chapter", "1")
        verses = passage.get("verses", [])

        for i, verse_text in enumerate(verses):
            passage_num = i + 1

            # First row gets metadata values, others get empty values
            if first_row:
                copyright_url = get_copyright_url(translation)
                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%f+00:00"
                )
                bygod_version = VERSION
                first_row = False
            else:
                copyright_url = ""
                timestamp = ""
                bygod_version = ""

            writer.writerow(
                [
                    book,
                    chapter,
                    passage_num,
                    language_abbr,
                    translation,
                    copyright_url,
                    timestamp,
                    bygod_version,
                ]
            )

    return output.getvalue()


def format_master_csv(data: List[Dict[str, Any]], translation: str) -> str:
    """
    Format master Bible data as CSV.

    Args:
        data: List of Bible passages
        translation: Translation abbreviation (e.g., 'ESV', 'NIV')

    Returns:
        Formatted CSV string
    """
    if not data:
        return "Book,Chapter,Passage,Language,Translation,Copyright,Timestamp,ByGod\n"

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Get language abbreviation (first 2 letters of language name)
    language = translation_info["language"]
    language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

    # Create CSV structure
    output = io.StringIO()
    writer = csv.writer(output)

    # Add headers
    writer.writerow(
        [
            "Book",
            "Chapter",
            "Passage",
            "Language",
            "Translation",
            "Copyright",
            "Timestamp",
            "ByGod",
        ]
    )

    # Add data rows
    first_row = True
    for passage in data:
        book = passage.get("book", "Unknown")
        chapter = passage.get("chapter", "1")
        verses = passage.get("verses", [])

        for i, verse_text in enumerate(verses):
            passage_num = i + 1

            # First row gets metadata values, others get empty values
            if first_row:
                copyright_url = get_copyright_url(translation)
                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%f+00:00"
                )
                bygod_version = VERSION
                first_row = False
            else:
                copyright_url = ""
                timestamp = ""
                bygod_version = ""

            writer.writerow(
                [
                    book,
                    chapter,
                    passage_num,
                    language_abbr,
                    translation,
                    copyright_url,
                    timestamp,
                    bygod_version,
                ]
            )

    return output.getvalue()
