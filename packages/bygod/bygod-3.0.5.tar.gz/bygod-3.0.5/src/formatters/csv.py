"""
CSV formatters for ByGoD.

This module contains functions for formatting Bible data into CSV format
with metadata headers and structured data.
"""

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.translations import BIBLE_TRANSLATIONS


def format_as_csv(data: List[Dict[str, Any]], translation: str = "NIV") -> str:
    """
    Format Bible data as CSV with metadata header.

    Args:
        data: List of Bible passage dictionaries
        translation: Bible translation code (e.g., "NIV")

    Returns:
        Formatted CSV string
    """
    if not data:
        return "error,No data to format\n"

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Create output buffer
    output = io.StringIO()
    writer = csv.writer(output)

    # Write metadata as comments
    writer.writerow([f"# Translation: {translation} ({translation_info['name']})"])
    writer.writerow([f"# Language: {translation_info['language']}"])
    writer.writerow([f"# Generated: {datetime.now(timezone.utc).isoformat()}"])
    writer.writerow([f"# Total Passages: {len(data)}"])
    writer.writerow([f"# Format: CSV"])
    writer.writerow([])  # Empty row for separation

    # Write headers
    if data:
        headers = ["book", "chapter", "verse", "text", "translation"]
        writer.writerow(headers)

        # Write data
        for passage in data:
            row = [
                passage.get("book", ""),
                passage.get("chapter", ""),
                passage.get("verse", ""),
                passage.get("text", ""),
                translation,
            ]
            writer.writerow(row)

    return output.getvalue()


def format_master_csv(all_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format multiple translations as a single CSV file.

    Args:
        all_data: Dictionary with translation codes as keys and Bible data as values

    Returns:
        Formatted CSV string
    """
    if not all_data:
        return "error,No data to format\n"

    # Create output buffer
    output = io.StringIO()
    writer = csv.writer(output)

    # Write metadata as comments
    writer.writerow([f"# Generated: {datetime.now(timezone.utc).isoformat()}"])
    writer.writerow([f"# Total Translations: {len(all_data)}"])
    writer.writerow([f"# Format: CSV"])
    writer.writerow([])  # Empty row for separation

    # Write headers
    headers = ["translation", "book", "chapter", "verse", "text"]
    writer.writerow(headers)

    # Write data for all translations
    for translation, data in all_data.items():
        for passage in data:
            row = [
                translation,
                passage.get("book", ""),
                passage.get("chapter", ""),
                passage.get("verse", ""),
                passage.get("text", ""),
            ]
            writer.writerow(row)

    return output.getvalue()
