"""
Bible processing functions for ByGoD.

This module contains functions for processing full Bible downloads for individual
translations.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

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
        start_time = time.time()
        translation_dir = Path(output_dir) / translation
        books_dir = translation_dir / "books"

        # Try to reuse existing per-book JSON files
        reused_count = 0
        missing_books: List[str] = []
        data: List[Dict[str, Any]] = []

        for book in BOOKS:
            book_json = books_dir / f"{book}.json"
            if book_json.exists():
                try:
                    with open(book_json, "r", encoding="utf-8") as f:
                        book_obj = json.load(f)
                    # Expect structure {"metadata": ..., "books": {book: [passages...]}}
                    passages = []
                    books_map = book_obj.get("books", {})
                    if book in books_map and isinstance(books_map[book], list):
                        passages = books_map[book]
                    if passages:
                        data.extend(passages)
                        reused_count += 1
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ Could not reuse existing file {book_json}: {e}")
            # If no usable file, mark missing
            missing_books.append(book)

        # Download any missing books
        if missing_books:
            logger.info(
                f"📥 {len(missing_books)} books not found on disk. Downloading missing books..."
            )
            downloaded = await download_bible_async(
                translation=translation,
                books=missing_books,
                max_concurrent_requests=rate_limit,
                max_retries=retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )
            if not downloaded:
                logger.error(
                    f"Failed to obtain missing books for {translation}; aborting full Bible creation"
                )
                return
            data.extend(downloaded)

        download_time = time.time() - start_time

        # Validate that all books are present in data; if any missing, abort
        present_books = {p.get("book") for p in data if p.get("book")}
        missing_after = [b for b in BOOKS if b not in present_books]
        if missing_after:
            logger.error(
                f"❌ Missing books in assembled data: {', '.join(missing_after)}. Skipping full Bible file creation."
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
                    f"Saved full Bible for {translation} in {fmt} format: {output_file}"
                )

            except Exception as e:
                logger.error(
                    f"Error saving full Bible for {translation} in {fmt} format: {e}"
                )

        logger.info(
            f"Completed full Bible assembly for {translation} in {download_time:.2f}s (reused {reused_count} books)"
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
) -> Dict[str, Any]:
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
    tasks: List[asyncio.Task] = []
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
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = 0
    failed_books: List[str] = []
    for res in results:
        if isinstance(res, Exception):
            # Unknown book in this context
            failed_books.append("<unknown>")
            continue
        if isinstance(res, tuple) and len(res) == 2:
            book_name, ok = res
            if ok:
                success_count += 1
            else:
                failed_books.append(book_name)
    return {"success_count": success_count, "failed_count": len(failed_books), "failed_books": failed_books}


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
) -> Tuple[str, bool]:
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
                    f"Saved {book} ({translation}) in {fmt} format: {output_file}"
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
