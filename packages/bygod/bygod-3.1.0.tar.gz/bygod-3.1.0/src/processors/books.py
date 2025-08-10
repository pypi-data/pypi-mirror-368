"""
Books processing functions for ByGoD.

This module contains functions for processing multiple book downloads in parallel.
"""

import asyncio
import logging
from typing import Any, Dict, List

from .book import book_processor


async def books_processor(
    translation: str,
    books: List[str],
    output_dir: str,
    formats: List[str],
    max_concurrent_requests: int,
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
        max_concurrent_requests: Maximum concurrent requests
        retries: Maximum retry attempts
        retry_delay: Delay between retries
        timeout: Request timeout
        logger: Logger instance
    """
    # Create tasks for all books
    tasks: List[asyncio.Task] = []
    for book in books:
        task = book_processor(
            translation=translation,
            book=book,
            output_dir=output_dir,
            formats=formats,
            max_concurrent_requests=max_concurrent_requests,
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
