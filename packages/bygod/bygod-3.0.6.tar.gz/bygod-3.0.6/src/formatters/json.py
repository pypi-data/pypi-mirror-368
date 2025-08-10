"""
JSON formatters for ByGoD.

This module contains functions for formatting Bible data into JSON format
with metadata and structured organization.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.translations import BIBLE_TRANSLATIONS


def format_as_json(data: List[Dict[str, Any]], translation: str = "NIV") -> str:
    """
    Format Bible data as JSON with metadata.

    Args:
        data: List of Bible passage dictionaries
        translation: Bible translation code (e.g., "NIV")

    Returns:
        Formatted JSON string
    """
    if not data:
        return json.dumps({"error": "No data to format"}, indent=2)

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Create metadata
    metadata = {
        "translation": {
            "code": translation,
            "name": translation_info["name"],
            "language": translation_info["language"],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_passages": len(data),
        "format": "json",
    }

    # Group data by book
    books = {}
    for passage in data:
        book = passage.get("book", "Unknown")
        if book not in books:
            books[book] = []
        books[book].append(passage)

    # Create final structure
    result = {"metadata": metadata, "books": books}

    return json.dumps(result, indent=2, ensure_ascii=False)


def format_master_json(all_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format multiple translations as a single JSON file.

    Args:
        all_data: Dictionary with translation codes as keys and Bible data as values

    Returns:
        Formatted JSON string
    """
    if not all_data:
        return json.dumps({"error": "No data to format"}, indent=2)

    # Create metadata
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_translations": len(all_data),
        "translations": {},
    }

    # Add translation info to metadata
    for translation, data in all_data.items():
        translation_info = BIBLE_TRANSLATIONS.get(
            translation, {"name": translation, "language": "Unknown"}
        )
        metadata["translations"][translation] = {
            "name": translation_info["name"],
            "language": translation_info["language"],
            "total_passages": len(data),
        }

    # Create final structure
    result = {"metadata": metadata, "translations": {}}

    # Add each translation's data
    for translation, data in all_data.items():
        # Group data by book
        books = {}
        for passage in data:
            book = passage.get("book", "Unknown")
            if book not in books:
                books[book] = []
            books[book].append(passage)

        result["translations"][translation] = {"books": books}

    return json.dumps(result, indent=2, ensure_ascii=False)
