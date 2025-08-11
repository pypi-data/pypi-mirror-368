"""
CLI and configuration constants.

This module contains URL templates, HTTP configuration, and other constants
used throughout the Bible downloader command-line interface.
"""

# Bible Gateway URL template for passage lookup
PASSAGE_URL_TEMPLATE = "https://www.biblegateway.com/passage/?search={}&version={}"

# Default HTTP headers for requests
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Default timeout settings (in seconds)
DEFAULT_TIMEOUT = 300
DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_READ_TIMEOUT = 300

# Default retry settings
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2

# Default concurrency settings
DEFAULT_MAX_CONCURRENT_REQUESTS = 10

# Rate limiting settings
RATE_LIMIT_DELAY = 1.0  # Delay between requests in seconds
RATE_LIMIT_BURST_SIZE = 10  # Number of requests before rate limiting kicks in
REQUEST_DELAY = 0.01  # 10ms delay between requests (much faster)

# File output settings
DEFAULT_OUTPUT_FORMAT = "json"
SUPPORTED_OUTPUT_FORMATS = ["json", "csv", "xml", "yaml"]

# Logging settings
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
