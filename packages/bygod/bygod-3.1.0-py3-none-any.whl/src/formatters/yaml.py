"""
YAML formatters for ByGoD.

This module contains functions for formatting Bible data into YAML format
with metadata and structured organization.
"""

import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..constants.books import BOOKS
from ..constants.translations import BIBLE_TRANSLATIONS
from ..constants.copyright import get_copyright_url


def format_as_yaml(data: List[Dict[str, Any]], translation: str) -> str:
    """
    Format Bible data as YAML.

    Args:
        data: List of Bible passages
        translation: Translation abbreviation (e.g., 'ESV', 'NIV')

    Returns:
        Formatted YAML string
    """
    if not data:
        return yaml.dump({"error": "No data to format"}, default_flow_style=False)

    # Get translation info
    translation_info = BIBLE_TRANSLATIONS.get(
        translation, {"name": translation, "language": "Unknown"}
    )

    # Get language abbreviation (first 2 letters of language name)
    language = translation_info["language"]
    language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

    # Create the main structure: language_abbr -> translation_abbr -> book -> chapter -> verse
    result = {language_abbr: {translation: {}}}

    # Group data by book and chapter
    for passage in data:
        book = passage.get("book", "Unknown")
        chapter = passage.get("chapter", "1")
        verses = passage.get("verses", [])

        if book not in result[language_abbr][translation]:
            result[language_abbr][translation][book] = {}

        # Add chapter with verses
        result[language_abbr][translation][book][chapter] = {}
        for i, verse_text in enumerate(verses):
            verse_num = i + 1
            result[language_abbr][translation][book][chapter][
                str(verse_num)
            ] = verse_text

    # Add metadata section
    copyright_url = get_copyright_url(translation)
    result["meta"] = {
        "Copyright": copyright_url,
        "Language": language,
        "ByGod": "3.1.0",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        "Translation": translation,
    }

    return yaml.dump(result, default_flow_style=False, allow_unicode=True)


def format_master_yaml(all_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format multiple translations as a single YAML file.

    Args:
        all_data: Dictionary with translation codes as keys and Bible data as values

    Returns:
        Formatted YAML string
    """
    if not all_data:
        return yaml.dump({"error": "No data to format"}, default_flow_style=False)

    # Group translations by language
    languages = {}
    for translation, data in all_data.items():
        translation_info = BIBLE_TRANSLATIONS.get(
            translation, {"name": translation, "language": "Unknown"}
        )
        language = translation_info["language"]
        language_abbr = language[:2].upper() if len(language) >= 2 else language.upper()

        if language_abbr not in languages:
            languages[language_abbr] = {}

        # Add translation data
        languages[language_abbr][translation] = {}

        # Group data by book and chapter
        for passage in data:
            book = passage.get("book", "Unknown")
            chapter = passage.get("chapter", "1")
            verses = passage.get("verses", [])

            if book not in languages[language_abbr][translation]:
                languages[language_abbr][translation][book] = {}

            # Add chapter with verses
            languages[language_abbr][translation][book][chapter] = {}
            for i, verse_text in enumerate(verses):
                verse_num = i + 1
                languages[language_abbr][translation][book][chapter][
                    str(verse_num)
                ] = verse_text

    # Create final structure
    result = languages.copy()

    # Add metadata section
    result["meta"] = {
        "Copyright": "https://www.biblegateway.com/versions/",
        "Language": "Multiple",
        "ByGod": "3.1.0",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
        "Translation": "Multiple",
    }

    return yaml.dump(result, default_flow_style=False, allow_unicode=True)
