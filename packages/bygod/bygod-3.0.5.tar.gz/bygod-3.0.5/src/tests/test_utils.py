"""
Tests for utility functions.

This module contains tests for formatting and logging utilities.
"""

import logging
import os
import tempfile
from unittest.mock import patch

import pytest

from ..utils.formatting import format_duration, format_number_with_commas
from ..utils.logging import setup_logging


class TestFormatting:
    """Test cases for formatting utilities."""

    def test_format_duration_seconds(self):
        """Test formatting duration less than 60 seconds."""
        assert format_duration(30.5) == "30.5s"
        assert format_duration(0.1) == "0.1s"
        assert format_duration(59.9) == "59.9s"

    def test_format_duration_minutes(self):
        """Test formatting duration between 60 seconds and 1 hour."""
        assert format_duration(90) == "1m 30.0s"
        assert format_duration(125.7) == "2m 5.7s"
        assert format_duration(3599) == "59m 59.0s"

    def test_format_duration_hours(self):
        """Test formatting duration over 1 hour."""
        assert format_duration(3661) == "1h, 1m 1.0s"
        assert format_duration(7325) == "2h, 2m 5.0s"
        assert format_duration(3600) == "1h, 0m 0.0s"

    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "0.0s"

    def test_format_number_with_commas(self):
        """Test formatting numbers with commas."""
        assert format_number_with_commas(1234) == "1,234"
        assert format_number_with_commas(1234567) == "1,234,567"
        assert format_number_with_commas(0) == "0"
        assert format_number_with_commas(100) == "100"
        assert format_number_with_commas(999999999) == "999,999,999"


class TestLogging:
    """Test cases for logging utilities."""

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()

        assert logger.name == "bible_downloader"
        assert logger.level <= logging.DEBUG

        # Check that we have a console handler
        handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(handlers) > 0

    def test_setup_logging_custom_name(self):
        """Test setup_logging with custom logger name."""
        logger = setup_logging(name="test_logger")
        assert logger.name == "test_logger"

    def test_setup_logging_verbose_levels(self):
        """Test setup_logging with different verbose levels."""
        # Test verbose=0 (WARNING level)
        logger = setup_logging(verbose=0)
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert console_handlers[0].level == logging.WARNING

        # Test verbose=1 (INFO level)
        logger = setup_logging(verbose=1)
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert console_handlers[0].level == logging.INFO

        # Test verbose=2 (DEBUG level)
        logger = setup_logging(verbose=2)
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert console_handlers[0].level == logging.DEBUG

    def test_setup_logging_quiet_mode(self):
        """Test setup_logging with quiet mode."""
        logger = setup_logging(quiet=True)
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert console_handlers[0].level == logging.ERROR
        assert logger.level == logging.ERROR

    def test_setup_logging_explicit_level(self):
        """Test setup_logging with explicit log level."""
        logger = setup_logging(log_level="WARNING")
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert console_handlers[0].level == logging.WARNING

    def test_setup_logging_error_file(self):
        """Test setup_logging with error file logging."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            logger = setup_logging(error_log_file=temp_file_path)

            # Check that we have both console and file handlers
            console_handlers = [
                h for h in logger.handlers if isinstance(h, logging.StreamHandler)
            ]
            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]

            assert len(console_handlers) > 0
            assert len(file_handlers) > 0
            assert file_handlers[0].level == logging.ERROR

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_setup_logging_duplicate_handlers(self):
        """Test that setup_logging doesn't create duplicate handlers."""
        logger1 = setup_logging(name="test_duplicate")
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_logging(name="test_duplicate")
        assert len(logger2.handlers) == initial_handler_count

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level."""
        with pytest.raises(AttributeError):
            setup_logging(log_level="INVALID_LEVEL")

    def test_setup_logging_error_file_directory_creation(self):
        """Test that setup_logging creates directories for error files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            error_file_path = os.path.join(temp_dir, "logs", "errors.log")

            logger = setup_logging(error_log_file=error_file_path)

            # Check that the directory was created
            assert os.path.exists(os.path.dirname(error_file_path))

            # Check that we have a file handler
            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) > 0
