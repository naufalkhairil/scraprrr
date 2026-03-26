"""
Utility functions for Traveloka hotel scraper.

This module provides helper functions for file operations, output generation,
and other common tasks.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def generate_output_filename(
    prefix: str,
    extension: str,
    output_dir: str = ".",
    timestamp: Optional[datetime] = None,
    location: Optional[str] = None,
) -> str:
    """
    Generate a standardized output filename.

    Args:
        prefix: Filename prefix (e.g., 'trave_hotel_results').
        extension: File extension (e.g., 'csv', 'json').
        output_dir: Directory to save the file.
        timestamp: Timestamp to include in filename. Uses current time if None.
        location: Location name to include in filename.

    Returns:
        Full path to the output file.
    """
    from datetime import datetime

    if timestamp is None:
        timestamp = datetime.now()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Build filename
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
    parts = [prefix]

    if location:
        # Sanitize location name for filename
        safe_location = location.replace(" ", "_").replace("/", "_").lower()
        parts.append(safe_location)

    parts.append(timestamp_str)

    filename = "_".join(parts) + f".{extension}"
    filepath = os.path.join(output_dir, filename)

    logger.debug(f"Generated output filename: {filepath}")
    return filepath


def save_to_csv(data: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save data to CSV file using pandas.

    Args:
        data: List of dictionaries to save.
        filepath: Path to the output CSV file.
    """
    try:
        import csv
        import pandas as pd

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

        df = pd.DataFrame(data)
        # Use QUOTE_ALL to properly handle newlines and special characters in data
        df.to_csv(filepath, index=False, quoting=csv.QUOTE_ALL, escapechar="\\")
        logger.info(f"Data saved to CSV: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")
        raise


def save_to_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to JSON file.

    Args:
        data: Dictionary to save.
        filepath: Path to the output JSON file.
    """
    import json

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Data saved to JSON: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        raise
