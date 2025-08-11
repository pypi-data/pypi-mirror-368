"""
Logging utilities.

This module contains the logging setup and configuration functions.
"""

import logging
import os

import colorlog


def setup_logging(
    name: str = "bible_downloader",
    verbose: int = 0,
    quiet: bool = False,
    log_level: str = "INFO",
    error_log_file: str = None,
) -> logging.Logger:
    """
    Set up colored logging for the downloader with configurable verbosity and error logging.

    Args:
        name: Logger name
        verbose: Verbosity level (0=WARNING, 1=INFO, 2=DEBUG, 3+=ALL)
        quiet: Suppress all output except errors
        log_level: Explicit log level override
        error_log_file: File to log errors to in clean format

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)

    # Determine log level based on verbosity and quiet flags
    if quiet:
        console_level = logging.ERROR
    elif verbose == 0:
        console_level = logging.WARNING
    elif verbose == 1:
        console_level = logging.INFO
    elif verbose >= 2:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO

    # Override with explicit log level if provided
    if (
        log_level and log_level != "INFO"
    ):  # Only override if explicitly set to something other than default
        console_level = getattr(logging, log_level.upper())

    # Clear existing handlers to ensure clean setup
    logger.handlers.clear()

    # Create console handler with color
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(console_level)

    # Set logger level based on quiet mode
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.DEBUG)

    # Create formatter for console
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add error file handler if specified
    if error_log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(error_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(error_log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.ERROR)

        # Clean format for error file (no colors, more detailed)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"📝 Error logging enabled: {error_log_file}")

    return logger
