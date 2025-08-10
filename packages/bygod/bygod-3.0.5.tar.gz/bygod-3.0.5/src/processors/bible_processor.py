"""
Bible processing functions for ByGoD.

This module contains functions for processing full Bible downloads for individual
translations.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..constants.books import BOOKS
from ..constants.translations import BIBLE_TRANSLATIONS
from ..core.downloader import download_bible_async
from ..formatters import format_as_csv, format_as_json, format_as_xml, format_as_yaml


async def process_full_bible(
    translation: str,
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> None:
    """
    Process a full Bible download for a translation.

    Args:
        translation: Bible translation code (e.g., "NIV")
        output_dir: Output directory path
        formats: List of output formats
        rate_limit: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    logger.info(f"Downloading full Bible for {translation}...")

    try:
        # Download the full Bible
        start_time = time.time()
        data = await download_bible_async(
            translation=translation,
            max_concurrent_requests=rate_limit,
            max_retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        download_time = time.time() - start_time

        if not data:
            logger.error(f"Failed to download full Bible for {translation}")
            return

        # Create output directory
        translation_dir = Path(output_dir) / translation
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
                    f"Saved full Bible for {translation} in {fmt} format: {output_file}"
                )

            except Exception as e:
                logger.error(
                    f"Error saving full Bible for {translation} in {fmt} format: {e}"
                )

        logger.info(
            f"Completed full Bible download for {translation} in {download_time:.2f}s"
        )

    except Exception as e:
        logger.error(f"Error processing full Bible for {translation}: {e}")


async def process_books_parallel(
    translation: str,
    books: List[str],
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> None:
    """
    Process multiple books in parallel for a translation.

    Args:
        translation: Bible translation code (e.g., "NIV")
        books: List of book names to download
        output_dir: Output directory path
        formats: List of output formats
        rate_limit: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    # Create tasks for all books
    tasks = []
    for book in books:
        task = process_single_book(
            translation=translation,
            book=book,
            output_dir=output_dir,
            formats=formats,
            rate_limit=rate_limit,
            retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
            logger=logger,
        )
        tasks.append(task)

    # Execute all tasks concurrently
    await asyncio.gather(*tasks, return_exceptions=True)


async def process_single_book(
    translation: str,
    book: str,
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> None:
    """
    Process a single book download for a translation.

    Args:
        translation: Bible translation code (e.g., "NIV")
        book: Book name to download
        output_dir: Output directory path
        formats: List of output formats
        rate_limit: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    try:
        # Download the book
        start_time = time.time()
        data = await download_bible_async(
            translation=translation,
            books=[book],
            max_concurrent_requests=rate_limit,
            max_retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        download_time = time.time() - start_time

        if not data:
            logger.error(f"Failed to download {book} ({translation})")
            return

        # Create output directory structure
        translation_dir = Path(output_dir) / translation
        books_dir = translation_dir / "books"
        books_dir.mkdir(parents=True, exist_ok=True)

        # Save in all requested formats
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
                    f"Saved {book} ({translation}) in {fmt} format: {output_file}"
                )

            except Exception as e:
                logger.error(
                    f"Error saving {book} ({translation}) in {fmt} format: {e}"
                )

        pass

    except Exception as e:
        logger.error(f"Error processing {book} ({translation}): {e}")
