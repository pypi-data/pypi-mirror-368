#!/usr/bin/env python3
"""
ByGoD

A comprehensive, truly asynchronous tool for downloading Bible translations from
BibleGateway.com in multiple formats (JSON, CSV, YAML, XML) with genuine parallel
downloads, retry mechanisms, and flexible output options.

This module provides:
- True async HTTP requests with aiohttp for genuine parallelism
- Direct HTML parsing from BibleGateway (bypassing synchronous libraries)
- Support for multiple Bible translations simultaneously
- Output in various formats (JSON, CSV, YAML, XML)
- Intelligent rate limiting and retry mechanisms
- Organized output in structured directories
- Comprehensive logging and progress tracking

Author: ByGoD Team
License: MIT
Version: 3.1.0 - CLI Improvements Edition
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import List

# Import modular components
from src.cli.parser import parse_args
from src.constants.books import BOOKS
from src.processors.books import books_processor
from src.processors.bible import bible_processor
from src.processors.translations import translations_combine_processor
from src.utils.formatting import format_duration
from src.utils.logging import setup_logging


async def main_async():
    """Orchestrate the Bible download process asynchronously."""
    # Parse command-line arguments
    args = parse_args()

    # Set up logging
    logger = setup_logging(
        name="bible_downloader",
        verbose=args.verbose,
        quiet=args.quiet,
        log_level=args.log_level,
        error_log_file=args.log_errors,
    )

    # Log startup information
    logger.info("🚀 ByGoD")
    logger.info(f"📚 Translations: {', '.join(args.translations)}")
    logger.info(f"📖 Books: {args.books if args.books else 'All books'}")
    logger.info(f"📄 Formats: {', '.join(args.formats)}")
    logger.info(f"📁 Output Directory: {args.output}")
    logger.info(f"⚡ Concurrency: {args.concurrency} concurrent requests")
    logger.info(f"🔄 Retries: {args.retries} (delay: {args.delay}s)")
    logger.info(f"⏱️ Timeout: {args.timeout}s")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse books if specified
    books_to_download = None
    if args.books:
        books_to_download = [book.strip() for book in args.books.split(",")]
        # Validate books
        invalid_books = [book for book in books_to_download if book not in BOOKS]
        if invalid_books:
            logger.error(f"Invalid books: {', '.join(invalid_books)}")
            logger.error(f"Valid books: {', '.join(BOOKS)}")
            return 1

    # Handle combined file generation
    if args.combined:
        if len(args.translations) < 2:
            logger.error("Combined file requires at least 2 translations")
            return 1
        logger.info("🔄 Processing combined file...")
        await translations_combine_processor(
            translations=args.translations,
            output_dir=str(output_dir),
            formats=args.formats,
            max_concurrent_requests=args.concurrency,
            retries=args.retries,
            retry_delay=args.delay,
            timeout=args.timeout,
            logger=logger,
        )
        return 0

    # Process each translation
    start_time = time.time()
    failed_translations = []
    for translation in args.translations:
        try:
            logger.info(f"📖 Processing {translation}")
            translation_dir = output_dir / translation
            books_dir = translation_dir / "books"

            if books_to_download:
                # Download only selected books
                result = await books_processor(
                    translation=translation,
                    books=books_to_download,
                    output_dir=str(output_dir),
                    formats=args.formats,
                    max_concurrent_requests=args.concurrency,
                    retries=args.retries,
                    retry_delay=args.delay,
                    timeout=args.timeout,
                    logger=logger,
                )
                if result and isinstance(result, dict):
                    logger.info(
                        f"📦 Summary for {translation}: {result.get('success_count', 0)} books saved, {result.get('failed_count', 0)} failed"
                    )
                # Intelligent assemble: create full Bible only if all books are present on disk
                all_exist = all((books_dir / f"{book}.json").exists() for book in BOOKS)
                if all_exist:
                    await bible_processor(
                        translation=translation,
                        output_dir=str(output_dir),
                        formats=args.formats,
                        max_concurrent_requests=args.concurrency,
                        retries=args.retries,
                        retry_delay=args.delay,
                        timeout=args.timeout,
                        logger=logger,
                    )
            else:
                # No specific books requested: download all books, then assemble full Bible
                result = await books_processor(
                    translation=translation,
                    books=BOOKS,
                    output_dir=str(output_dir),
                    formats=args.formats,
                    max_concurrent_requests=args.concurrency,
                    retries=args.retries,
                    retry_delay=args.delay,
                    timeout=args.timeout,
                    logger=logger,
                )
                if result and isinstance(result, dict):
                    logger.info(
                        f"📦 Summary for {translation}: {result.get('success_count', 0)} books saved, {result.get('failed_count', 0)} failed"
                    )
                # After downloading all books, assemble the full Bible from existing files
                await bible_processor(
                    translation=translation,
                    output_dir=str(output_dir),
                    formats=args.formats,
                    max_concurrent_requests=args.concurrency,
                    retries=args.retries,
                    retry_delay=args.delay,
                    timeout=args.timeout,
                    logger=logger,
                )
        except Exception as e:
            logger.error(f"❌ Error processing {translation}: {e}")
            failed_translations.append(translation)
    # Log completion summary
    total_time = time.time() - start_time
    successful_translations = [
        t for t in args.translations if t not in failed_translations
    ]
    logger.info(
        f"⏱️ Total Time: {format_duration(total_time)}, Successful translations: {len(successful_translations)}, Failed translations: {len(failed_translations)}"
    )
    return 0 if not failed_translations else 1


def main():
    """Execute the ByGoD application."""
    try:
        # Run the async main function
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
