"""
CLI parser and validation for ByGoD.

This module contains functions for parsing command-line arguments and validating
user input for the Bible downloader application.
"""

import argparse
import textwrap
from typing import List

from ..constants.books import BOOKS
from ..constants.cli import SUPPORTED_OUTPUT_FORMATS
from ..constants.translations import SUPPORTED_BIBLE_TRANSLATIONS


def validate_bibles(translations_str: str) -> List[str]:
    """
    Validate and parse Bible translation codes.

    Args:
        translations_str: Comma-separated string of translation codes

    Returns:
        List of validated translation codes

    Raises:
        argparse.ArgumentTypeError: If any translation code is invalid
    """
    translations = [t.strip().upper() for t in translations_str.split(",") if t.strip()]

    # Check if all translations are valid
    invalid_translations = [t for t in translations if t not in SUPPORTED_BIBLE_TRANSLATIONS]
    if invalid_translations:
        valid_translations = ", ".join(sorted(SUPPORTED_BIBLE_TRANSLATIONS.keys()))
        raise argparse.ArgumentTypeError(
            f"Invalid translation(s): {', '.join(invalid_translations)}. "
            f"Valid translations: {valid_translations}"
        )

    return translations


def validate_format(formats_str: str) -> List[str]:
    """
    Validate and parse output format codes.

    Args:
        formats_str: Comma-separated string of format codes

    Returns:
        List of validated format codes

    Raises:
        argparse.ArgumentTypeError: If any format code is invalid
    """
    formats = [f.strip().lower() for f in formats_str.split(",") if f.strip()]

    # Check if all formats are valid
    invalid_formats = [f for f in formats if f not in SUPPORTED_OUTPUT_FORMATS]
    if invalid_formats:
        valid_formats = ", ".join(SUPPORTED_OUTPUT_FORMATS)
        raise argparse.ArgumentTypeError(
            f"Invalid format(s): {', '.join(invalid_formats)}. "
            f"Valid formats: {valid_formats}"
        )

    return formats


def validate_output_mode(mode: str) -> str:
    """
    Validate output mode.

    Args:
        mode: Output mode string

    Returns:
        Validated output mode

    Raises:
        argparse.ArgumentTypeError: If mode is invalid
    """
    valid_modes = ["book", "books", "all"]
    if mode.lower() not in valid_modes:
        raise argparse.ArgumentTypeError(
            f"Invalid output mode: {mode}. Valid modes: {', '.join(valid_modes)}"
        )
    return mode.lower()


def parse_args():
    """
    Parse command-line arguments for ByGoD.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Download Bibles from BibleGateway.com with true async support",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Download NIV Bible in JSON format
  python main.py -t NIV -f json

  # Download multiple translations in all formats
  python main.py -t NIV,KJV,ESV -f json,csv,xml,yaml

  # Download specific books only
  python main.py -t NIV -b "Genesis,Psalms,Matthew"

  # Download with custom output directory and verbose logging
  python main.py -t NIV -o ./my_bibles -vv

  # Download with combined output file
  python main.py -t NIV,KJV --combined

  # Download with custom concurrency and retry settings
  python main.py -t NIV -c 3 --retries 5 --timeout 60

  # Download with specific output mode
  python main.py -t NIV -m books
        """,
    )

    # Translation selection
    wrapped_choices = textwrap.fill(", ".join(SUPPORTED_BIBLE_TRANSLATIONS.keys()), width=80)
    parser.add_argument(
        "-t",
        "--translations",
        type=validate_bibles,
        default=["NIV"],
        help=f"Select 1 or more translations to download from this list "
        f"(using comma separated values):\n{wrapped_choices}",
    )

    # Book selection
    parser.add_argument(
        "-b",
        "--books",
        type=str,
        help="Comma-separated list of specific books to download "
        "(e.g., 'Genesis,Psalms,Matthew'). If not specified, downloads all books.",
    )

    # Output formats
    parser.add_argument(
        "-f",
        "--formats",
        type=validate_format,
        default=["json"],
        help=f"Choose 1 or more formats (using comma separated values)\n"
        f"{', '.join(SUPPORTED_OUTPUT_FORMATS).upper()}",
    )

    # Output mode
    parser.add_argument(
        "-m",
        "--mode",
        type=validate_output_mode,
        default="all",
        choices=["book", "books", "all"],
        help="Output mode: 'book' for full Bible in a single file only, "
        "'books' for individual book files only, or 'all' for both "
        "individual book files and full Bible in a single file (default: all)",
    )

    # Output directory
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./bibles",
        help="Directory to save downloaded Bibles (default: ./bibles)",
    )

    # Combined output
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Generate a combined file containing all downloaded translations "
        "(only works when downloading multiple translations)",
    )

    # Concurrency and performance
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=5,
        help="Maximum concurrent requests to BibleGateway (default: 5)",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts for failed downloads (default: 3)",
    )

    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=2,
        help="Delay in seconds between retry attempts (default: 2)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds for HTTP requests (default: 300)",
    )

    # Logging and verbosity
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v: INFO, -vv: DEBUG, -vvv: TRACE)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )

    parser.add_argument(
        "-ll",
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-errors",
        type=str,
        help="Log errors to the specified file"
    )

    # Advanced options
    parser.add_argument(
        "-dr",
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )

    parser.add_argument(
        "-r",
        "--resume",
        action="store_true",
        help="Resume interrupted downloads by skipping existing files",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if files already exist",
    )

    return parser.parse_args()
