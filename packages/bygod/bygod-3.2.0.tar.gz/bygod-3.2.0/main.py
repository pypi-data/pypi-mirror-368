#!/usr/bin/env python3
"""
ByGoD - The Bible, By God - Bible Gateway Downloader

A comprehensive, truly asynchronous tool for downloading Bible translations
from BibleGateway.com in multiple formats (JSON, CSV, YAML, XML) with
genuine parallel downloads, retry mechanisms, and flexible output options.

Version: {VERSION} - CLI Improvements Edition
"""

import asyncio
import sys
import time
from pathlib import Path

from src.cli.parser import parse_args
from src.constants.books import BOOKS
from src.constants.version import VERSION
from src.processors.bible import bible_processor
from src.processors.books import books_processor
from src.processors.translations import translations_combine_processor
from src.utils.formatting import format_duration
from src.utils.logging import setup_logging


async def main_async():
    """
    Orchestrate the Bible download process asynchronously.

    This function handles three operation modes:
    - books: Download individual book files (all books by default, or use -b
      for specific books)
    - bible: Download entire Bible directly to a single file (most efficient
      for full Bible only)
    - bible-books: Download both individual books AND assemble the full Bible
      (most comprehensive)

    The function intelligently processes translations based on the selected
    mode, with optimized performance for Bible assembly when reusing existing
    book files.
    """
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
    logger.info(f"📋 Mode: {args.bygod}")
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

    # Process each translation based on operation mode
    start_time = time.time()
    failed_translations = []

    for translation in args.translations:
        try:
            logger.info(f"📖 Processing {translation}")

            # Mode: books - Download individual books only
            if args.bygod == "books":
                books_to_process = books_to_download if books_to_download else BOOKS
                result = await books_processor(
                    translation=translation,
                    books=books_to_process,
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
                        f"📦 Summary for {translation}: "
                        f"{result.get('success_count', 0)} books saved, "
                        f"{result.get('failed_count', 0)} failed"
                    )

            # Mode: bible - Download entire Bible to single file only
            elif args.bygod == "bible":
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

            # Mode: bible-books - Download both individual books AND entire
            # Bible
            elif args.bygod == "bible-books":
                # First download individual books
                books_to_process = books_to_download if books_to_download else BOOKS
                result = await books_processor(
                    translation=translation,
                    books=books_to_process,
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
                        f"📦 Summary for {translation}: "
                        f"{result.get('success_count', 0)} books saved, "
                        f"{result.get('failed_count', 0)} failed"
                    )

                # Then assemble full Bible from the downloaded books
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
        f"⏱️ Total Time: {format_duration(total_time)}, "
        f"Successful translations: {len(successful_translations)}, "
        f"Failed translations: {len(failed_translations)}"
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
