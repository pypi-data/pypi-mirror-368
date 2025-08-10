"""
Core downloader module.

This module contains the AsyncBibleDownloader class for downloading Bible content.
"""

import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from meaningless import JSONDownloader
from meaningless.utilities.common import get_page

from ..constants.books import BOOKS
from ..constants.chapters import CHAPTER_COUNTS
from ..constants.cli import (
    DEFAULT_HEADERS,
    DEFAULT_MAX_CONCURRENT_REQUESTS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    PASSAGE_URL_TEMPLATE,
    REQUEST_DELAY,
)
from ..constants.translations import BIBLE_TRANSLATIONS
from ..utils.formatting import format_duration, format_number_with_commas

# Mapping of our canonical book names to BibleGateway/meaningless expected names
BOOK_NAME_GATEWAY_ALIASES: Dict[str, str] = {
    "Song of Songs": "Song of Solomon",
}


class AsyncBibleDownloader:
    """
    True async Bible downloader that directly fetches from BibleGateway.

    This class bypasses synchronous libraries and makes direct HTTP requests
    to BibleGateway.com, parsing the HTML to extract Bible content. It provides
    genuine parallelism with asyncio and aiohttp.
    """

    def __init__(
        self,
        translation: str,
        max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: int = DEFAULT_RETRY_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the async Bible downloader.

        Args:
            translation: Bible translation code (e.g., "NIV", "KJV")
            max_concurrent_requests: Maximum concurrent HTTP requests
            max_retries: Maximum retry attempts per request
            retry_delay: Base delay between retries
            timeout: Request timeout in seconds
        """
        self.translation = translation.upper()
        self.max_concurrent_requests = max_concurrent_requests
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Validate translation
        if self.translation not in BIBLE_TRANSLATIONS:
            raise ValueError(f"Unsupported translation: {translation}")

        # Create semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Add small delay between requests to prevent overwhelming the server
        self.request_delay = REQUEST_DELAY

        # Session will be created when needed
        self.session: Optional[aiohttp.ClientSession] = None

        # Set up logging - use the main logger to ensure consistent verbosity
        self.logger = logging.getLogger("bible_downloader")
        # Track last failed books (for full-Bible runs)
        self._last_failed_books: List[str] = []

        # Store original get_page function for restoration
        self._original_get_page = get_page

        # Monkey patch get_page to use our async session
        self._setup_monkey_patch()

    @property
    def last_failed_books(self) -> List[str]:
        return self._last_failed_books

    def _setup_monkey_patch(self):
        """Set up monkey patching of meaningless library's get_page function."""
        import meaningless.utilities.common

        async def async_get_page(url: str) -> str:
            """Async version of get_page that uses our aiohttp session."""
            if not self.session:
                await self._create_session()

            async with self.semaphore:
                # Add small delay to prevent overwhelming the server
                await asyncio.sleep(self.request_delay)

                for retry in range(self.max_retries + 1):
                    try:
                        # Check if session is closed and recreate if needed
                        if self.session.closed:
                            await self._create_session()

                        async with self.session.get(url) as response:
                            if response.status == 200:
                                return await response.text()
                            elif response.status == 429:  # Rate limited
                                self.logger.warning(
                                    f"⏸️ Rate limited (429) for {self.translation}, retrying..."
                                )
                                if retry < self.max_retries:
                                    delay = self.retry_delay * (2**retry)
                                    await asyncio.sleep(delay)
                                    continue
                                else:
                                    self.logger.error(
                                        f"❌ Rate limited after {self.max_retries + 1} "
                                        f"retries for {self.translation}"
                                    )
                                    return ""
                            else:
                                self.logger.error(
                                    f"❌ HTTP {response.status} for {self.translation}"
                                )
                                return ""

                    except (
                        aiohttp.ClientError,
                        aiohttp.ServerDisconnectedError,
                        aiohttp.ClientOSError,
                        ConnectionError,
                    ) as e:
                        # Connection-related errors - recreate session and retry
                        if retry < self.max_retries:
                            delay = self.retry_delay * (2**retry)
                            self.logger.warning(
                                f"🔄 Connection error for {self.translation}, "
                                f"recreating session and retrying in {delay}s: {str(e)}"
                            )
                            # Close and recreate session
                            await self._close_session()
                            await asyncio.sleep(delay)
                            continue
                        else:
                            self.logger.error(
                                f"❌ Connection failed for {self.translation} "
                                f"after {self.max_retries + 1} attempts: {str(e)}"
                            )
                            return ""

                    except Exception as e:
                        if retry < self.max_retries:
                            delay = self.retry_delay * (2**retry)
                            self.logger.warning(
                                f"🔄 Request failed for {self.translation}, "
                                f"retrying in {delay}s: {str(e)}"
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            self.logger.error(
                                f"❌ Request failed for {self.translation} "
                                f"after {self.max_retries + 1} attempts: {str(e)}"
                            )
                            return ""

            return ""

        # Create a synchronous wrapper that runs the async function
        def sync_get_page(url: str) -> str:
            """Synchronous wrapper for async_get_page."""
            try:
                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_running_loop()
                    # If we're already in an async context, we can't use run_until_complete
                    # So we'll use the original get_page as fallback
                    return self._original_get_page(url)
                except RuntimeError:
                    # No event loop running, we can create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(async_get_page(url))
                    finally:
                        loop.close()
            except Exception as e:
                self.logger.error(f"Error in monkey-patched get_page: {e}")
                # Fallback to original
                return self._original_get_page(url)

        # Apply the monkey patch
        meaningless.utilities.common.get_page = sync_get_page
        self._patched_get_page = sync_get_page

    def _restore_original_get_page(self):
        """Restore the original get_page function."""
        import meaningless.utilities.common

        meaningless.utilities.common.get_page = self._original_get_page

    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
        self._restore_original_get_page()
        # Return None to indicate no exception handling
        return None

    async def _create_session(self):
        """Create aiohttp session with proper configuration."""
        timeout = ClientTimeout(total=self.timeout, connect=10, sock_read=15)
        connector = TCPConnector(
            limit=self.max_concurrent_requests * 4,  # Increased connection pool
            limit_per_host=self.max_concurrent_requests
            * 2,  # More per-host connections
            keepalive_timeout=self.timeout,  # Use timeout from --timeout flag
            enable_cleanup_closed=True,
            force_close=False,
            ttl_dns_cache=300,  # DNS caching
        )

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=DEFAULT_HEADERS,
        )

    async def _close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, url: str) -> Optional[str]:
        """
        Make a single HTTP request with retries and rate limiting.

        Args:
            url: URL to request

        Returns:
            HTML content as string, or None if failed
        """
        if not self.session:
            await self._create_session()

        async with self.semaphore:
            # Add small delay to prevent overwhelming the server
            await asyncio.sleep(self.request_delay)

            for retry in range(self.max_retries + 1):
                try:
                    # Check if session is closed and recreate if needed
                    if self.session.closed:
                        await self._create_session()

                    async with self.session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:  # Rate limited
                            self.logger.warning(
                                f"⏸️ Rate limited (429) for {self.translation}, retrying..."
                            )
                            if retry < self.max_retries:
                                delay = self.retry_delay * (2**retry)
                                await asyncio.sleep(delay)
                                continue
                            else:
                                self.logger.error(
                                    f"❌ Rate limited after {self.max_retries + 1} "
                                    f"retries for {self.translation}"
                                )
                                return None
                        else:
                            self.logger.error(
                                f"❌ HTTP {response.status} for {self.translation}"
                            )
                            return None

                except (
                    aiohttp.ClientError,
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientOSError,
                    ConnectionError,
                ) as e:
                    # Connection-related errors - recreate session and retry
                    if retry < self.max_retries:
                        delay = self.retry_delay * (2**retry)
                        self.logger.warning(
                            f"🔄 Connection error for {self.translation}, "
                            f"recreating session and retrying in {delay}s: {str(e)}"
                        )
                        # Close and recreate session
                        await self._close_session()
                        await asyncio.sleep(delay)
                        continue
                    else:
                        self.logger.error(
                            f"❌ Connection failed for {self.translation} "
                            f"after {self.max_retries + 1} attempts: {str(e)}"
                        )
                        return None

                except Exception as e:
                    if retry < self.max_retries:
                        delay = self.retry_delay * (2**retry)
                        self.logger.warning(
                            f"🔄 Request failed for {self.translation}, "
                            f"retrying in {delay}s: {str(e)}"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        self.logger.error(
                            f"❌ Request failed for {self.translation} "
                            f"after {self.max_retries + 1} attempts: {str(e)}"
                        )
                        return None

        return None

    def _gateway_book_name(self, book: str) -> str:
        """Return the book name expected by BibleGateway/meaningless for a given canonical name."""
        return BOOK_NAME_GATEWAY_ALIASES.get(book, book)

    def _candidate_book_names(self, book: str) -> List[str]:
        """Return ordered candidate names to try for a given book (canonical then alias)."""
        names: List[str] = [book]
        alias = BOOK_NAME_GATEWAY_ALIASES.get(book)
        if alias and alias not in names:
            names.append(alias)
        return names

    async def _discover_chapter_count(self, book: str) -> int:
        """
        Discover the number of chapters in a book.

        Args:
            book: Name of the book

        Returns:
            Number of chapters in the book
        """
        # Use known chapter counts first (fastest and most reliable)
        if book in CHAPTER_COUNTS:
            self.logger.debug(
                f"Using known chapter count for {book}: {CHAPTER_COUNTS[book]}"
            )
            return CHAPTER_COUNTS[book]

        # Fallback: try to get chapter count from the first chapter page (only if not in known list)
        self.logger.warning(
            f"⚠️ Book '{book}' not in known chapter list, attempting HTTP discovery..."
        )
        content = None
        for candidate in self._candidate_book_names(book):
            url = PASSAGE_URL_TEMPLATE.format(quote(f"{candidate} 1"), self.translation)
            content = await self._make_request(url)
            if content:
                break

        if not content:
            return 1  # Fallback to single chapter

        try:
            soup = BeautifulSoup(content, "html.parser")

            # Look for chapter navigation links - try multiple patterns
            chapter_links = []

            # Pattern 1: Direct chapter links
            chapter_links.extend(soup.find_all("a", href=re.compile(r"chapter=\d+")))

            # Pattern 2: Chapter navigation dropdown
            chapter_select = soup.find("select", {"name": "chapter"})
            if chapter_select:
                chapter_links.extend(chapter_select.find_all("option"))

            # Pattern 3: Chapter navigation in breadcrumbs or navigation
            nav_links = soup.find_all("a", href=re.compile(rf"{book.lower()}\+\d+"))
            chapter_links.extend(nav_links)

            if chapter_links:
                chapters = set()
                for link in chapter_links:
                    # Extract chapter number from href
                    href = link.get("href", "")
                    match = re.search(r"chapter=(\d+)", href)
                    if match:
                        chapters.add(int(match.group(1)))

                    # Extract from option value
                    value = link.get("value", "")
                    if value.isdigit():
                        chapters.add(int(value))

                    # Extract from text content
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        chapters.add(int(text))

                if chapters:
                    max_chapter = max(chapters)
                    self.logger.debug(f"Discovered {max_chapter} chapters for {book}")
                    return max_chapter

            # Fallback: try to find chapter numbers in the text
            chapter_pattern = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
            matches = chapter_pattern.findall(content)
            if matches:
                max_chapter = max(int(match) for match in matches)
                self.logger.debug(
                    f"Found {max_chapter} chapters via text pattern for {book}"
                )
                return max_chapter

        except Exception as e:
            self.logger.warning(f"⚠️ Error discovering chapters for {book}: {str(e)}")

        # Final fallback to single chapter
        return 1

    async def download_chapter(
        self, book: str, chapter: int
    ) -> Optional[Dict[str, Any]]:
        """
        Download a single chapter asynchronously using meaningless library's JSONDownloader.

        Args:
            book: Name of the book
            chapter: Chapter number

        Returns:
            Dictionary with chapter data, or None if failed
        """
        temp_dir = None
        try:
            # Capture start time right before the actual download begins
            chapter_start_time = time.time()

            # Log chapter start
            self.logger.info(f"📖 Starting {book} {chapter} ({self.translation})")

            # Use JSONDownloader directly - it handles all parsing through meaningless library
            downloader = JSONDownloader(
                translation=self.translation,
                show_passage_numbers=False,
                strip_excess_whitespace=True,
            )

            loop = asyncio.get_event_loop()

            verses: List[str] = []
            selected_key = None

            # Try canonical name first, then alias if needed
            for candidate in self._candidate_book_names(book):
                # Create a temporary directory for this attempt
                temp_dir = tempfile.mkdtemp(
                    prefix=f"bible_download_{self.translation}_{candidate}_{chapter}_"
                )
                downloader.default_directory = temp_dir

                # Run the synchronous download_chapter in a thread pool to avoid blocking
                result = await loop.run_in_executor(
                    None, downloader.download_chapter, candidate, chapter
                )

                if result != 1:
                    # Cleanup this attempt and try next candidate
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    temp_dir = None
                    continue

                # Read the downloaded JSON file (named after the candidate)
                json_file = os.path.join(temp_dir, f"{candidate}.json")
                if not os.path.exists(json_file):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    temp_dir = None
                    continue

                with open(json_file, "r", encoding="utf-8") as f:
                    book_data = json.load(f)

                # Resolve book key robustly: try canonical, candidate, then fuzzy match, then first key
                def _norm(s: str) -> str:
                    return "".join(ch.lower() for ch in s if ch.isalnum())

                selected_key = None
                if isinstance(book_data, dict):
                    keys = list(book_data.keys())
                    norm_to_key = {_norm(k): k for k in keys}
                    for target in [book, candidate]:
                        nk = _norm(target)
                        if nk in norm_to_key:
                            selected_key = norm_to_key[nk]
                            break
                    if selected_key is None and keys:
                        selected_key = keys[0]

                verses = []
                if selected_key is not None and isinstance(book_data[selected_key], dict):
                    book_chapters = book_data[selected_key]
                    # Normalize chapter keys to ints for comparison
                    int_key_map = {}
                    for k, v in book_chapters.items():
                        try:
                            int_key_map[int(k)] = v
                        except Exception:
                            continue
                    if chapter in int_key_map:
                        chapter_verses = int_key_map[chapter]
                        # chapter_verses keys may be strings or ints; sort as ints
                        sorted_keys = []
                        for vk in chapter_verses.keys():
                            try:
                                sorted_keys.append(int(vk))
                            except Exception:
                                pass
                        for verse_num in sorted(sorted_keys):
                            verse_text = chapter_verses[str(verse_num)] if str(verse_num) in chapter_verses else chapter_verses.get(verse_num)
                            if verse_text:
                                verses.append(verse_text)

                if verses:
                    break
                else:
                    # Cleanup and try next candidate
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    temp_dir = None

            if not verses:
                self.logger.warning(
                    f"⚠️ No verses found for {book} {chapter} ({self.translation})"
                )
                return None

            end_time = time.time()
            duration = end_time - chapter_start_time
            self.logger.info(
                f"✅ Downloaded {book} {chapter} ({self.translation}): "
                f"{format_number_with_commas(len(verses))} verses"
            )

            return {"book": book, "chapter": str(chapter), "verses": verses}

        except Exception as e:
            self.logger.error(
                f"❌ Error downloading {book} {chapter} ({self.translation}): {e}"
            )
            return None
        finally:
            # Clean up the temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.logger.warning(
                        f"Could not clean up temp directory {temp_dir}: {e}"
                    )

    async def download_book(self, book: str) -> List[Dict[str, Any]]:
        """
        Download an entire book asynchronously with all chapters in parallel.

        Args:
            book: Name of the book to download

        Returns:
            List of chapter dictionaries
        """
        book_start_time = time.time()
        self.logger.info(f"📚 Starting download of {book} ({self.translation})")

        # Discover chapter count (now instant for known books)
        chapter_count = await self._discover_chapter_count(book)
        self.logger.debug(f"📊 {book} has {chapter_count} chapters")

        # Create tasks for all chapters
        tasks = [
            self.download_chapter(book, chapter)
            for chapter in range(1, chapter_count + 1)
        ]

        # Execute all chapter downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        chapters = []
        successful_chapters = 0
        failed_chapters = 0

        for i, result in enumerate(results):
            chapter_num = i + 1
            if isinstance(result, Exception):
                self.logger.error(
                    f"Error downloading {book} {chapter_num} ({self.translation}): {result}"
                )
                failed_chapters += 1
            elif result:
                chapters.append(result)
                successful_chapters += 1
                self.logger.debug(
                    f"✅ Downloaded {book} {chapter_num} ({self.translation}): "
                    f"{len(result['verses'])} verses"
                )
            else:
                self.logger.warning(
                    f"❌ Failed to download {book} {chapter_num} ({self.translation})"
                )
                failed_chapters += 1

        total_verses = sum(len(chapter["verses"]) for chapter in chapters)
        book_duration = time.time() - book_start_time
        self.logger.info(
            f"📊 Completed {book} ({self.translation}): "
            f"{successful_chapters}/{chapter_count} chapters, "
            f"{format_number_with_commas(total_verses)} total verses in "
            f"{format_duration(book_duration)}"
        )

        if failed_chapters > 0:
            self.logger.warning(
                f"⚠️ {failed_chapters} chapters failed to download for "
                f"{book} ({self.translation})"
            )

        return chapters

    async def download_full_bible(self) -> List[Dict[str, Any]]:
        """
        Download the entire Bible asynchronously with all books and chapters in parallel.

        Returns:
            List of all chapter dictionaries
        """
        self.logger.info(f"🚀 Starting full Bible download for {self.translation}")
        self.logger.info(f"📚 Total books to download: {len(BOOKS)}")

        # Create tasks for all books
        tasks = [self.download_book(book) for book in BOOKS]

        self.logger.info(f"⚡ Executing {len(tasks)} concurrent book downloads")

        # Execute all book downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        all_chapters = []
        successful_books = 0
        failed_books = 0
        failed_book_names: List[str] = []

        for i, result in enumerate(results):
            book = BOOKS[i]
            if isinstance(result, Exception):
                self.logger.error(
                    f"❌ Error downloading {book} ({self.translation}): {result}"
                )
                failed_books += 1
                failed_book_names.append(book)
            elif result:
                all_chapters.extend(result)
                successful_books += 1
                total_verses = sum(len(chapter["verses"]) for chapter in result)
                self.logger.info(
                    f"✅ Downloaded {book} ({self.translation}): "
                    f"{len(result)} chapters, {total_verses} verses"
                )
            else:
                self.logger.warning(
                    f"❌ Failed to download {book} ({self.translation})"
                )
                failed_books += 1
                failed_book_names.append(book)

        total_verses = sum(len(chapter["verses"]) for chapter in all_chapters)
        self.logger.info(f"📊 Full Bible download complete for {self.translation}")
        self.logger.info(f"📚 Books: {successful_books}/{len(BOOKS)} successful")
        self.logger.info(f"📖 Chapters: {len(all_chapters)} total")
        self.logger.info(f"📝 Verses: {total_verses} total")

        if failed_books > 0:
            self.logger.warning(f"⚠️ {failed_books} books failed to download")
            self.logger.warning(
                f"⚠️ Failed books: {', '.join(failed_book_names)}"
            )
        # Record failures for the caller to decide whether to save
        self._last_failed_books = failed_book_names

        return all_chapters


async def download_bible_async(
    translation: str,
    books: Optional[List[str]] = None,
    max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: int = DEFAULT_RETRY_DELAY,
    timeout: int = DEFAULT_TIMEOUT,
) -> List[Dict[str, Any]]:
    """
    Convenience function to download Bible content asynchronously.

    Args:
        translation: Bible translation code
        books: List of books to download (None for all books)
        max_concurrent_requests: Maximum concurrent HTTP requests
        max_retries: Maximum retry attempts per request
        retry_delay: Base delay between retries
        timeout: Request timeout in seconds

    Returns:
        List of chapter dictionaries
    """
    if books is None:
        books = BOOKS

    logger = logging.getLogger("download_bible_async")
    logger.info(f"🔤 Starting download for translation: {translation}")
    logger.info(f"📚 Books to download: {len(books)}")
    if len(books) <= 10:
        logger.info(f"📖 Books: {', '.join(books)}")
    else:
        logger.info(f"📖 Books: {', '.join(books[:5])}... and {len(books) - 5} more")

    async with AsyncBibleDownloader(
        translation=translation,
        max_concurrent_requests=max_concurrent_requests,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
    ) as downloader:
        if len(books) == 1:
            # Single book download
            return await downloader.download_book(books[0])
        elif len(books) == len(BOOKS):
            # Full Bible download
            result = await downloader.download_full_bible()
            # If any book failed, signal failure upstream by returning empty
            if downloader.last_failed_books:
                logging.getLogger("download_bible_async").error(
                    f"❌ Full Bible download had failures: {', '.join(downloader.last_failed_books)}. Skipping file creation."
                )
                return []
            return result
        else:
            # Multiple books download
            tasks = [downloader.download_book(book) for book in books]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_chapters = []
            for i, result in enumerate(results):
                book = books[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ Error downloading {book}: {result}")
                elif result:
                    all_chapters.extend(result)
                else:
                    logger.warning(f"❌ Failed to download {book}")

            return all_chapters
