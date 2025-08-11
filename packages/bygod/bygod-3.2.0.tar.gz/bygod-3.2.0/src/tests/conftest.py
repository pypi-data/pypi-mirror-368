"""
Pytest configuration and common fixtures.

This module contains pytest configuration and shared fixtures for all tests.
"""

import asyncio
import tempfile
from unittest.mock import AsyncMock

import pytest

from ..constants.books import BOOKS, NEW_TESTAMENT_BOOKS, OLD_TESTAMENT_BOOKS
from ..constants.translations import BIBLE_TRANSLATIONS


@pytest.fixture
def sample_bible_data():
    """Sample Bible data for testing."""
    return [
        {
            "book": "Genesis",
            "chapter": "1",
            "verses": [
                "In the beginning God created the heavens and the earth.",
                "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters.",
                "And God said, 'Let there be light,' and there was light.",
            ],
        },
        {
            "book": "Genesis",
            "chapter": "2",
            "verses": [
                "Thus the heavens and the earth were completed in all their vast array.",
                "By the seventh day God had finished the work he had been doing; so on the seventh day he rested from all his work.",
            ],
        },
    ]


@pytest.fixture
def sample_translation():
    """Sample translation code for testing."""
    return "NIV"


@pytest.fixture
def sample_book():
    """Sample book name for testing."""
    return "Genesis"


@pytest.fixture
def sample_books():
    """Sample list of books for testing."""
    return ["Genesis", "Exodus", "Psalms"]


@pytest.fixture
def temp_dir():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing."""
    mock_session = AsyncMock()
    mock_session.closed = False
    return mock_session


@pytest.fixture
def mock_aiohttp_response():
    """Mock aiohttp response for testing."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<html>Test content</html>")
    return mock_response


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing."""
    return """
    <html>
        <body>
            <div class="passage-content">
                <div class="verse">
                    <span class="verse-number">1</span>
                    <span class="verse-text">In the beginning God created the heavens and the earth.</span>
                </div>
                <div class="verse">
                    <span class="verse-number">2</span>
                    <span class="verse-text">Now the earth was formless and empty, darkness was over the surface of the deep.</span>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {
        "Genesis": {
            "1": {
                "1": "In the beginning God created the heavens and the earth.",
                "2": "Now the earth was formless and empty, darkness was over the surface of the deep.",
            },
            "2": {
                "1": "Thus the heavens and the earth were completed in all their vast array."
            },
        }
    }


@pytest.fixture
def all_translations():
    """All available translations for testing."""
    return list(BIBLE_TRANSLATIONS.keys())


@pytest.fixture
def all_books():
    """All available books for testing."""
    return BOOKS.copy()


@pytest.fixture
def old_testament_books():
    """Old Testament books for testing."""
    return OLD_TESTAMENT_BOOKS.copy()


@pytest.fixture
def new_testament_books():
    """New Testament books for testing."""
    return NEW_TESTAMENT_BOOKS.copy()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# Async test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
