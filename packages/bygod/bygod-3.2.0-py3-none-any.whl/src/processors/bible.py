"""
Bible processor module for ByGoD.

This module handles the assembly of full Bibles from individual book files,
with intelligent reuse of existing downloaded books for optimal performance.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from ..constants.books import BOOKS
from ..core.downloader import download_bible_async
from ..formatters.csv import format_as_csv
from ..formatters.json import format_as_json
from ..formatters.xml import format_as_xml
from ..formatters.yaml import format_as_yaml


async def bible_processor(
    translation: str,
    output_dir: str,
    formats: List[str],
    max_concurrent_requests: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger,
) -> None:
    """
    Process full Bible assembly for a translation.

    This function efficiently assembles a full Bible by:
    1. First checking for existing book files in the output directory
    2. Only downloading missing books if necessary
    3. Assembling the full Bible from available data

    Args:
        translation: Bible translation code (e.g., "NIV")
        output_dir: Output directory path
        formats: List of output formats
        max_concurrent_requests: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    logger.info(f"📚 Assembling full Bible for {translation}")

    try:
        start_time = time.time()
        translation_dir = Path(output_dir) / translation
        books_dir = translation_dir / "books"

        # First, check for existing book files in the output directory
        # This is more efficient than checking download locations
        reused_count = 0
        missing_books: List[str] = []
        data: List[Dict[str, Any]] = []

        logger.info(f"🔍 Checking for existing book files in {books_dir}")

        for book in BOOKS:
            # Check for any format of the book file (prioritize JSON for
            # consistency)
            book_json = books_dir / f"{book}.json"

            if book_json.exists():
                try:
                    with open(book_json, "r", encoding="utf-8") as f:
                        book_obj = json.load(f)

                    # Extract passages from the book data
                    passages = []

                    # Parse the actual JSON structure: language_abbr -> translation -> book -> chapter -> verse
                    for language_abbr in book_obj:
                        if language_abbr == "meta":
                            continue
                        for trans_abbr in book_obj[language_abbr]:
                            if book in book_obj[language_abbr][trans_abbr]:
                                book_data = book_obj[language_abbr][trans_abbr][book]
                                # Convert the book data back to the expected passage format
                                for chapter_num, chapter_verses in book_data.items():
                                    for verse_num, verse_text in chapter_verses.items():
                                        passages.append({
                                            "book": book,
                                            "chapter": chapter_num,
                                            "verses": [verse_text]
                                        })
                                break

                    if passages:
                        data.extend(passages)
                        reused_count += 1
                        logger.debug(
                            f"✅ Reused existing {book} ({len(passages)} "
                            f"passages)"
                        )
                        continue
                    else:
                        logger.warning(
                            f"⚠️ Found {book}.json but no valid passages"
                        )

                except Exception as e:
                    logger.warning(
                        f"⚠️ Could not read existing file {book_json}: {e}"
                    )

            # If no usable file found, mark as missing
            missing_books.append(book)
            logger.debug(f"❌ Missing book: {book}")

        # Download any missing books
        if missing_books:
            logger.info(
                f"📥 {len(missing_books)} books not found. "
                f"Downloading missing books: {', '.join(missing_books)}"
            )
            downloaded = await download_bible_async(
                translation=translation,
                books=missing_books,
                max_concurrent_requests=max_concurrent_requests,
                max_retries=retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )
            if not downloaded:
                logger.error(
                    f"Failed to obtain missing books for {translation}; "
                    f"aborting full Bible creation"
                )
                return
            data.extend(downloaded)
            logger.info(f"✅ Downloaded {len(missing_books)} missing books")
        else:
            logger.info(
                f"🎉 All {reused_count} books found locally - "
                f"no downloads needed!"
            )

        # Validate that all books are present in data; if any missing, abort
        present_books = {p.get("book") for p in data if p.get("book")}
        missing_after = [b for b in BOOKS if b not in present_books]
        if missing_after:
            logger.error(
                f"❌ Missing books in assembled data: "
                f"{', '.join(missing_after)}. Skipping full Bible file "
                f"creation."
            )
            return

        # Ensure output directory exists
        translation_dir.mkdir(parents=True, exist_ok=True)

        # Save in all requested formats
        for fmt in formats:
            try:
                if fmt == "json":
                    formatted_data = format_as_json(data, translation)
                    output_file = translation_dir / "bible.json"
                elif fmt == "csv":
                    formatted_data = format_as_csv(data, translation)
                    output_file = translation_dir / "bible.csv"
                elif fmt == "xml":
                    formatted_data = format_as_xml(data, translation)
                    output_file = translation_dir / "bible.xml"
                elif fmt == "yaml":
                    formatted_data = format_as_yaml(data, translation)
                    output_file = translation_dir / "bible.yml"
                else:
                    continue

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(formatted_data)

                logger.debug(
                    f"✅ Saved full Bible for {translation} in {fmt} format: "
                    f"{output_file}"
                )

            except Exception as e:
                logger.error(
                    f"❌ Error saving full Bible for {translation} in {fmt} "
                    f"format: {e}"
                )

        total_time = time.time() - start_time
        logger.info(
            f"🎯 Completed full Bible assembly for {translation} in "
            f"{total_time:.2f}s"
        )

    except Exception as e:
        logger.error(f"❌ Error processing full Bible for {translation}: {e}")
        raise
