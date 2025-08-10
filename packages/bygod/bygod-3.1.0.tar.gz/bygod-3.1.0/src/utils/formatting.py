"""
Formatting utilities for ByGoD.

This module contains utility functions for formatting durations, numbers, and other
display elements.
"""


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format (e.g., 1h, 12m, 34s).

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h, {remaining_minutes}m {remaining_seconds:.1f}s"


def format_number_with_commas(number: int) -> str:
    """
    Format number with comma separators (e.g., 1,234,567).

    Args:
        number: Number to format

    Returns:
        Formatted number string with commas
    """
    return f"{number:,}"
