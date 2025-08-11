"""
Tests for the core downloader functionality.

This module contains tests for the AsyncBibleDownloader class and related functions.
"""

from unittest.mock import AsyncMock, patch

import pytest

from ..constants.books import BOOKS
from ..constants.translations import BIBLE_TRANSLATIONS
from ..core.downloader import AsyncBibleDownloader, download_bible_async


class TestAsyncBibleDownloader:
    """Test cases for AsyncBibleDownloader class."""

    def test_init_valid_translation(self):
        """Test initialization with valid translation."""
        downloader = AsyncBibleDownloader("NIV")
        assert downloader.translation == "NIV"
        assert downloader.max_concurrent_requests == 10
        assert downloader.max_retries == 3
        assert downloader.retry_delay == 2
        assert downloader.timeout == 300

    def test_init_invalid_translation(self):
        """Test initialization with invalid translation raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported translation"):
            AsyncBibleDownloader("INVALID")

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        downloader = AsyncBibleDownloader(
            "KJV",
            max_concurrent_requests=10,
            max_retries=5,
            retry_delay=3,
            timeout=600,
        )
        assert downloader.translation == "KJV"
        assert downloader.max_concurrent_requests == 10
        assert downloader.max_retries == 5
        assert downloader.retry_delay == 3
        assert downloader.timeout == 600

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        downloader = AsyncBibleDownloader("NIV")

        async with downloader as d:
            assert d is downloader
            assert downloader.session is not None

        assert downloader.session is None

    @pytest.mark.asyncio
    async def test_discover_chapter_count_known_book(self):
        """Test chapter count discovery for known books."""
        downloader = AsyncBibleDownloader("NIV")

        # Test a known book
        chapter_count = await downloader._discover_chapter_count("Genesis")
        assert chapter_count == 50

    @pytest.mark.asyncio
    async def test_discover_chapter_count_unknown_book(self):
        """Test chapter count discovery for unknown books."""
        downloader = AsyncBibleDownloader("NIV")

        # Mock the _make_request method to return a simple HTML
        with patch.object(
            downloader, "_make_request", return_value="<html>Chapter 1</html>"
        ):
            chapter_count = await downloader._discover_chapter_count("UnknownBook")
            assert chapter_count == 1  # Should fallback to 1

    @pytest.mark.skip(reason="Complex async mocking issue - needs investigation")
    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful HTTP request."""
        downloader = AsyncBibleDownloader("NIV")

        # Mock the semaphore to avoid blocking
        mock_semaphore = AsyncMock()
        mock_semaphore.__aenter__ = AsyncMock(return_value=None)
        mock_semaphore.__aexit__ = AsyncMock(return_value=None)
        downloader.semaphore = mock_semaphore

        # Mock the session and response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Success</html>")

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.closed = False

        # Set the session directly
        downloader.session = mock_session

        result = await downloader._make_request("http://example.com")
        assert result == "<html>Success</html>"

    @pytest.mark.asyncio
    async def test_make_request_rate_limited(self):
        """Test handling of rate limiting (429 status)."""
        downloader = AsyncBibleDownloader("NIV")

        # Mock the session and response
        mock_response = AsyncMock()
        mock_response.status = 429

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.closed = False

        downloader.session = mock_session

        result = await downloader._make_request("http://example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_make_request_connection_error(self):
        """Test handling of connection errors."""
        downloader = AsyncBibleDownloader("NIV")

        # Mock the session to raise a connection error
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_session.closed = False

        downloader.session = mock_session

        result = await downloader._make_request("http://example.com")
        assert result is None


class TestDownloadBibleAsync:
    """Test cases for download_bible_async function."""

    @pytest.mark.asyncio
    async def test_download_bible_async_single_book(self):
        """Test downloading a single book."""
        with patch("src.core.downloader.AsyncBibleDownloader") as mock_downloader_class:
            mock_downloader = AsyncMock()
            mock_downloader_class.return_value.__aenter__.return_value = mock_downloader

            # Mock the download_book method
            mock_downloader.download_book.return_value = [
                {"book": "Genesis", "chapter": "1", "verses": ["In the beginning..."]}
            ]

            result = await download_bible_async("NIV", books=["Genesis"])

            mock_downloader.download_book.assert_called_once_with("Genesis")
            assert len(result) == 1
            assert result[0]["book"] == "Genesis"

    @pytest.mark.asyncio
    async def test_download_bible_async_full_bible(self):
        """Test downloading the full Bible."""
        with patch("src.core.downloader.AsyncBibleDownloader") as mock_downloader_class:
            mock_downloader = AsyncMock()
            mock_downloader_class.return_value.__aenter__.return_value = mock_downloader

            # Mock the download_full_bible method
            mock_downloader.download_full_bible.return_value = [
                {"book": "Genesis", "chapter": "1", "verses": ["In the beginning..."]}
            ]

            # Mock the last_failed_books property to return empty list (no failures)
            mock_downloader.last_failed_books = []

            result = await download_bible_async("NIV", books=BOOKS)

            mock_downloader.download_full_bible.assert_called_once()
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_download_bible_async_multiple_books(self):
        """Test downloading multiple books."""
        with patch("src.core.downloader.AsyncBibleDownloader") as mock_downloader_class:
            mock_downloader = AsyncMock()
            mock_downloader_class.return_value.__aenter__.return_value = mock_downloader

            # Mock the download_book method
            mock_downloader.download_book.return_value = [
                {"book": "Genesis", "chapter": "1", "verses": ["In the beginning..."]}
            ]

            result = await download_bible_async("NIV", books=["Genesis", "Exodus"])

            assert mock_downloader.download_book.call_count == 2
            assert len(result) == 2


class TestConstants:
    """Test cases for constants."""

    def test_bible_translations_structure(self):
        """Test that BIBLE_TRANSLATIONS has the correct structure."""
        for code, info in BIBLE_TRANSLATIONS.items():
            assert isinstance(code, str)
            assert isinstance(info, dict)
            assert "name" in info
            assert "language" in info
            assert isinstance(info["name"], str)
            assert isinstance(info["language"], str)

    def test_books_list_structure(self):
        """Test that BOOKS list has the correct structure."""
        assert isinstance(BOOKS, list)
        assert len(BOOKS) == 66  # Should have 66 books

        for book in BOOKS:
            assert isinstance(book, str)
            assert len(book) > 0

    def test_books_contains_expected_books(self):
        """Test that BOOKS contains expected books."""
        expected_books = ["Genesis", "Exodus", "Psalms", "Matthew", "Revelation"]
        for book in expected_books:
            assert book in BOOKS

    def test_translations_contains_expected_translations(self):
        """Test that BIBLE_TRANSLATIONS contains expected translations."""
        expected_translations = ["NIV", "KJV", "ESV"]
        for translation in expected_translations:
            assert translation in BIBLE_TRANSLATIONS
