"""
Book processing functions for ByGoD.

This module contains functions for processing individual book downloads.
"""

import logging
from pathlib import Path
from typing import List, Tuple

from ..core.downloader import download_bible_async
from ..formatters import format_as_csv, format_as_json, format_as_xml, format_as_yaml


async def book_processor(
    translation: str,
    book: str,
    output_dir: str,
    formats: List[str],
    max_concurrent_requests: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> Tuple[str, bool]:
    """
    Process a single book download for a translation.

    Args:
        translation: Bible translation code (e.g., "NIV")
        book: Book name to download
        output_dir: Output directory path
        formats: List of output formats
        max_concurrent_requests: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    try:
        # Download the book

        data = await download_bible_async(
            translation=translation,
            books=[book],
            max_concurrent_requests=max_concurrent_requests,
            max_retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        # download_time = time.time() - start_time  # Unused variable

        if not data:
            logger.error(f"Failed to download {book} ({translation})")
            return (book, False)

        # Create output directory structure
        translation_dir = Path(output_dir) / translation
        books_dir = translation_dir / "books"
        books_dir.mkdir(parents=True, exist_ok=True)

        # Save in all requested formats; success if at least one saves
        saved_any = False
        for fmt in formats:
            try:
                if fmt == "json":
                    formatted_data = format_as_json(data, translation)
                    output_file = books_dir / f"{book}.json"
                elif fmt == "csv":
                    formatted_data = format_as_csv(data, translation)
                    output_file = books_dir / f"{book}.csv"
                elif fmt == "xml":
                    formatted_data = format_as_xml(data, translation)
                    output_file = books_dir / f"{book}.xml"
                elif fmt == "yaml":
                    formatted_data = format_as_yaml(data, translation)
                    output_file = books_dir / f"{book}.yml"
                else:
                    continue

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(formatted_data)

                logger.debug(
                    f"💾 Saved {book} ({translation}) in {fmt} format: {output_file}"
                )
                saved_any = True

            except Exception as e:
                logger.error(
                    f"Error saving {book} ({translation}) in {fmt} format: {e}"
                )

        return (book, saved_any)

    except Exception as e:
        logger.error(f"Error processing {book} ({translation}): {e}")
        return (book, False)
