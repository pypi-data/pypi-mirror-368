"""
Tests for constants.

This module contains tests for Bible translations and books constants.
"""

from ..constants.books import (
    BOOKS,
    NEW_TESTAMENT_BOOKS,
    NEW_TESTAMENT_BOOKS_COUNT,
    OLD_TESTAMENT_BOOKS,
    OLD_TESTAMENT_BOOKS_COUNT,
    TOTAL_BOOKS,
)
from ..constants.chapters import (
    CHAPTER_COUNTS,
    NEW_TESTAMENT_CHAPTERS,
    NEW_TESTAMENT_CHAPTERS_TOTAL,
    OLD_TESTAMENT_CHAPTERS,
    OLD_TESTAMENT_CHAPTERS_TOTAL,
    TOTAL_CHAPTERS,
)
from ..constants.translations import BIBLE_TRANSLATIONS


class TestBibleTranslations:
    """Test cases for BIBLE_TRANSLATIONS constant."""

    def test_translations_structure(self):
        """Test that all translations have the correct structure."""
        for code, info in BIBLE_TRANSLATIONS.items():
            # Check code format
            assert isinstance(code, str)
            assert len(code) > 0
            assert code.isupper()

            # Check info structure
            assert isinstance(info, dict)
            assert "name" in info
            assert "language" in info

            # Check data types
            assert isinstance(info["name"], str)
            assert isinstance(info["language"], str)
            assert len(info["name"]) > 0
            assert len(info["language"]) > 0

    def test_required_translations(self):
        """Test that all required translations are present."""
        required_translations = [
            "NIV",
            "KJV",
            "ESV",
            "NKJV",
            "NLT",
            "CSB",
            "NASB",
            "RSV",
            "ASV",
            "WEB",
            "YLT",
            "AMP",
            "MSG",
            "CEV",
            "ERV",
            "GW",
            "HCSB",
            "ICB",
            "ISV",
            "LEB",
            "NCV",
            "NET",
            "NIRV",
            "NRSV",
            "TLB",
            "TLV",
            "VOICE",
            "WYC",
        ]

        for translation in required_translations:
            assert (
                translation in BIBLE_TRANSLATIONS
            ), f"Missing translation: {translation}"

    def test_translation_names(self):
        """Test that translation names are meaningful."""
        # Check a few key translations
        assert BIBLE_TRANSLATIONS["NIV"]["name"] == "New International Version"
        assert BIBLE_TRANSLATIONS["KJV"]["name"] == "King James Version"
        assert BIBLE_TRANSLATIONS["ESV"]["name"] == "English Standard Version"
        assert BIBLE_TRANSLATIONS["NKJV"]["name"] == "New King James Version"

    def test_language_consistency(self):
        """Test that all translations have consistent language information."""
        # All translations should be English for now
        for code, info in BIBLE_TRANSLATIONS.items():
            assert (
                info["language"] == "English"
            ), f"Translation {code} has non-English language: {info['language']}"

    def test_no_duplicate_codes(self):
        """Test that there are no duplicate translation codes."""
        codes = list(BIBLE_TRANSLATIONS.keys())
        unique_codes = set(codes)
        assert len(codes) == len(unique_codes), "Duplicate translation codes found"

    def test_no_duplicate_names(self):
        """Test that there are no duplicate translation names."""
        names = [info["name"] for info in BIBLE_TRANSLATIONS.values()]
        unique_names = set(names)
        assert len(names) == len(unique_names), "Duplicate translation names found"


class TestBooks:
    """Test cases for BOOKS constant."""

    def test_books_structure(self):
        """Test that BOOKS has the correct structure."""
        assert isinstance(BOOKS, list)
        assert len(BOOKS) == 66, f"Expected 66 books, got {len(BOOKS)}"

        for book in BOOKS:
            assert isinstance(book, str)
            assert len(book) > 0
            assert book.strip() == book  # No leading/trailing whitespace

    def test_old_testament_books(self):
        """Test that all Old Testament books are present."""
        old_testament_books = [
            "Genesis",
            "Exodus",
            "Leviticus",
            "Numbers",
            "Deuteronomy",
            "Joshua",
            "Judges",
            "Ruth",
            "1 Samuel",
            "2 Samuel",
            "1 Kings",
            "2 Kings",
            "1 Chronicles",
            "2 Chronicles",
            "Ezra",
            "Nehemiah",
            "Esther",
            "Job",
            "Psalms",
            "Proverbs",
            "Ecclesiastes",
            "Song of Songs",
            "Isaiah",
            "Jeremiah",
            "Lamentations",
            "Ezekiel",
            "Daniel",
            "Hosea",
            "Joel",
            "Amos",
            "Obadiah",
            "Jonah",
            "Micah",
            "Nahum",
            "Habakkuk",
            "Zephaniah",
            "Haggai",
            "Zechariah",
            "Malachi",
        ]

        for book in old_testament_books:
            assert book in BOOKS, f"Missing Old Testament book: {book}"

    def test_new_testament_books(self):
        """Test that all New Testament books are present."""
        new_testament_books = [
            "Matthew",
            "Mark",
            "Luke",
            "John",
            "Acts",
            "Romans",
            "1 Corinthians",
            "2 Corinthians",
            "Galatians",
            "Ephesians",
            "Philippians",
            "Colossians",
            "1 Thessalonians",
            "2 Thessalonians",
            "1 Timothy",
            "2 Timothy",
            "Titus",
            "Philemon",
            "Hebrews",
            "James",
            "1 Peter",
            "2 Peter",
            "1 John",
            "2 John",
            "3 John",
            "Jude",
            "Revelation",
        ]

        for book in new_testament_books:
            assert book in BOOKS, f"Missing New Testament book: {book}"

    def test_book_order(self):
        """Test that books are in canonical order."""
        # Check first few books
        assert BOOKS[0] == "Genesis"
        assert BOOKS[1] == "Exodus"
        assert BOOKS[2] == "Leviticus"

        # Check last few books
        assert BOOKS[-3] == "3 John"
        assert BOOKS[-2] == "Jude"
        assert BOOKS[-1] == "Revelation"

    def test_no_duplicate_books(self):
        """Test that there are no duplicate books."""
        unique_books = set(BOOKS)
        assert len(BOOKS) == len(unique_books), "Duplicate books found"

    def test_book_names_format(self):
        """Test that book names follow expected format."""
        for book in BOOKS:
            # Books should not be empty or just whitespace
            assert (
                book.strip() == book
            ), f"Book name has leading/trailing whitespace: '{book}'"

            # Books should not contain only numbers
            assert not book.isdigit(), f"Book name should not be only digits: {book}"

            # Books should have at least one letter
            assert any(
                c.isalpha() for c in book
            ), f"Book name should contain at least one letter: {book}"

    def test_specific_book_names(self):
        """Test specific book names that might have variations."""
        # Check for correct naming of books that might have variations
        assert "Song of Songs" in BOOKS  # Not "Song of Solomon"
        assert "1 Samuel" in BOOKS  # Not "First Samuel"
        assert "2 Samuel" in BOOKS  # Not "Second Samuel"
        assert "1 John" in BOOKS  # Not "First John"
        assert "2 John" in BOOKS  # Not "Second John"
        assert "3 John" in BOOKS  # Not "Third John"


class TestConstantsIntegration:
    """Integration tests for constants."""

    def test_translations_and_books_consistency(self):
        """Test that translations and books work together."""
        # This is a basic integration test
        assert len(BIBLE_TRANSLATIONS) > 0, "No translations defined"
        assert len(BOOKS) == 66, "Incorrect number of books"

        # All translations should be able to work with all books
        for translation_code in BIBLE_TRANSLATIONS:
            assert isinstance(translation_code, str)
            assert len(translation_code) > 0

        for book_name in BOOKS:
            assert isinstance(book_name, str)
            assert len(book_name) > 0

    def test_chapter_counts_consistency(self):
        """Test that chapter counts are consistent with book lists."""
        # All books should have chapter counts
        for book in BOOKS:
            assert book in CHAPTER_COUNTS, f"Missing chapter count for {book}"
            assert isinstance(
                CHAPTER_COUNTS[book], int
            ), f"Chapter count for {book} is not an integer"
            assert (
                CHAPTER_COUNTS[book] > 0
            ), f"Chapter count for {book} must be positive"

        # All chapter counts should correspond to books
        for book in CHAPTER_COUNTS:
            assert book in BOOKS, f"Chapter count for unknown book: {book}"

    def test_testament_organization(self):
        """Test that testament organization is correct."""
        # Test book counts
        assert TOTAL_BOOKS == 66, f"Expected 66 total books, got {TOTAL_BOOKS}"
        assert (
            OLD_TESTAMENT_BOOKS_COUNT == 39
        ), f"Expected 39 OT books, got {OLD_TESTAMENT_BOOKS_COUNT}"
        assert (
            NEW_TESTAMENT_BOOKS_COUNT == 27
        ), f"Expected 27 NT books, got {NEW_TESTAMENT_BOOKS_COUNT}"

        # Test that counts add up
        assert OLD_TESTAMENT_BOOKS_COUNT + NEW_TESTAMENT_BOOKS_COUNT == TOTAL_BOOKS

        # Test book lists
        assert len(OLD_TESTAMENT_BOOKS) == 39
        assert len(NEW_TESTAMENT_BOOKS) == 27
        assert len(OLD_TESTAMENT_BOOKS) + len(NEW_TESTAMENT_BOOKS) == len(BOOKS)

    def test_chapter_count_totals(self):
        """Test that chapter count totals are correct."""
        # Test that totals are calculated correctly
        assert sum(CHAPTER_COUNTS.values()) == TOTAL_CHAPTERS
        assert sum(OLD_TESTAMENT_CHAPTERS.values()) == OLD_TESTAMENT_CHAPTERS_TOTAL
        assert sum(NEW_TESTAMENT_CHAPTERS.values()) == NEW_TESTAMENT_CHAPTERS_TOTAL

        # Test that testament totals add up to total
        assert (
            OLD_TESTAMENT_CHAPTERS_TOTAL + NEW_TESTAMENT_CHAPTERS_TOTAL
            == TOTAL_CHAPTERS
        )

        # Verify some known totals
        assert (
            TOTAL_CHAPTERS == 1189
        ), f"Expected 1189 total chapters, got {TOTAL_CHAPTERS}"
        assert (
            OLD_TESTAMENT_CHAPTERS_TOTAL == 929
        ), f"Expected 929 OT chapters, got {OLD_TESTAMENT_CHAPTERS_TOTAL}"
        assert (
            NEW_TESTAMENT_CHAPTERS_TOTAL == 260
        ), f"Expected 260 NT chapters, got {NEW_TESTAMENT_CHAPTERS_TOTAL}"

    def test_testament_chapter_consistency(self):
        """Test that testament chapter dictionaries are consistent."""
        # All OT books should be in OT chapters
        for book in OLD_TESTAMENT_BOOKS:
            assert (
                book in OLD_TESTAMENT_CHAPTERS
            ), f"OT book {book} missing from OT chapters"
            assert (
                OLD_TESTAMENT_CHAPTERS[book] == CHAPTER_COUNTS[book]
            ), f"Chapter count mismatch for {book}"

        # All NT books should be in NT chapters
        for book in NEW_TESTAMENT_BOOKS:
            assert (
                book in NEW_TESTAMENT_CHAPTERS
            ), f"NT book {book} missing from NT chapters"
            assert (
                NEW_TESTAMENT_CHAPTERS[book] == CHAPTER_COUNTS[book]
            ), f"Chapter count mismatch for {book}"

        # No overlap between OT and NT chapters
        ot_books = set(OLD_TESTAMENT_CHAPTERS.keys())
        nt_books = set(NEW_TESTAMENT_CHAPTERS.keys())
        assert not (ot_books & nt_books), "Overlap between OT and NT books"
