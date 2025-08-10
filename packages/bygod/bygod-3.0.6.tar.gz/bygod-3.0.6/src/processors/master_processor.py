"""
Master processing functions for ByGoD.

This module contains functions for processing multiple translations and creating
combined output files containing all translations.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..constants.translations import BIBLE_TRANSLATIONS
from ..core.downloader import download_bible_async
from ..formatters import (
    format_master_csv,
    format_master_json,
    format_master_xml,
    format_master_yaml,
)


def combine_existing_translations(
    translations: List[str],
    output_dir: str,
    formats: List[str],
    logger: logging.Logger,
    filename: str = "bible_combined",
) -> bool:
    """
    Combine existing translation files into a master file.

    Args:
        translations: List of translation codes
        output_dir: Output directory path
        formats: List of output formats
        logger: Logger instance
        filename: Base filename for combined file

    Returns:
        True if combination was successful, False otherwise
    """
    if len(translations) < 2:
        logger.warning("⚠️ Need at least 2 translations to create combined file")
        return False

    # Check if all translation files exist
    all_data = {}
    for translation in translations:
        translation_dir = Path(output_dir) / translation

        # Look for full Bible files
        found_files = []
        for fmt in formats:
            if fmt == "json":
                full_file = translation_dir / "bible.json"
            elif fmt == "csv":
                full_file = translation_dir / "bible.csv"
            elif fmt == "xml":
                full_file = translation_dir / "bible.xml"
            elif fmt == "yaml":
                full_file = translation_dir / "bible.yml"
            else:
                continue

            if full_file.exists():
                found_files.append((fmt, full_file))
                break

        if not found_files:
            logger.warning(f"⚠️ No full Bible file found for {translation}")
            return False

        # Load the first available format
        fmt, file_path = found_files[0]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if fmt == "json":
                    data = json.load(f)
                    # Extract passages from the data structure
                    passages = []
                    if "books" in data:
                        for book_data in data["books"].values():
                            passages.extend(book_data)
                    else:
                        passages = data.get("passages", [])
                    all_data[translation] = passages
                else:
                    logger.warning(
                        f"⚠️ Loading {fmt} format for combination not supported yet"
                    )
                    return False

        except Exception as e:
            logger.error(f"❌ Error loading {translation} data: {e}")
            return False

    # Create combined files
    success = True
    for fmt in formats:
        try:
            if fmt == "json":
                formatted_data = format_master_json(all_data)
                output_file = Path(output_dir) / f"{filename}.json"
            elif fmt == "csv":
                formatted_data = format_master_csv(all_data)
                output_file = Path(output_dir) / f"{filename}.csv"
            elif fmt == "xml":
                formatted_data = format_master_xml(all_data)
                output_file = Path(output_dir) / f"{filename}.xml"
            elif fmt == "yaml":
                formatted_data = format_master_yaml(all_data)
                output_file = Path(output_dir) / f"{filename}.yml"
            else:
                continue

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_data)

            logger.info(f"📄 Created combined file: {output_file}")

        except Exception as e:
            logger.error(f"❌ Error creating combined {fmt} file: {e}")
            success = False

    return success


async def process_master_file(
    translations: List[str],
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
    filename: str = "bible_combined",
) -> None:
    """
    Process multiple translations and create a combined master file.

    Args:
        translations: List of translation codes
        output_dir: Output directory path
        formats: List of output formats
        rate_limit: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
        filename: Base filename for combined file
    """
    if len(translations) < 2:
        logger.warning("⚠️ Need at least 2 translations to create combined file")
        return

    # Download all translations
    all_data = {}
    failed_translations = []

    for translation in translations:
        try:
            start_time = time.time()

            data = await download_bible_async(
                translation=translation,
                max_concurrent_requests=rate_limit,
                max_retries=retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )

            download_time = time.time() - start_time

            if data:
                all_data[translation] = data
                logger.info(f"✅ Downloaded {translation} in {download_time:.2f}s")
            else:
                failed_translations.append(translation)
                logger.error(f"❌ Failed to download {translation}")

        except Exception as e:
            failed_translations.append(translation)
            logger.error(f"❌ Error downloading {translation}: {e}")

    if failed_translations:
        logger.warning(f"⚠️ Failed translations: {', '.join(failed_translations)}")
        if len(all_data) < 2:
            logger.error("❌ Not enough successful downloads to create combined file")
            return

    # Create combined files
    success = True
    for fmt in formats:
        try:
            if fmt == "json":
                formatted_data = format_master_json(all_data)
                output_file = Path(output_dir) / f"{filename}.json"
            elif fmt == "csv":
                formatted_data = format_master_csv(all_data)
                output_file = Path(output_dir) / f"{filename}.csv"
            elif fmt == "xml":
                formatted_data = format_master_xml(all_data)
                output_file = Path(output_dir) / f"{filename}.xml"
            elif fmt == "yaml":
                formatted_data = format_master_yaml(all_data)
                output_file = Path(output_dir) / f"{filename}.yml"
            else:
                continue

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_data)

            logger.info(f"📄 Created combined file: {output_file}")

        except Exception as e:
            logger.error(f"❌ Error creating combined {fmt} file: {e}")
            success = False

    if success:
        logger.info(
            f"🎉 Successfully created combined files for {len(all_data)} translations"
        )
    else:
        logger.error("❌ Some combined files failed to create")


# Import time module for timing
import time
