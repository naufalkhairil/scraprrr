"""
Utility functions for Traveloka scrapers.

This module provides helper functions for file operations, data processing,
and other common tasks used across flight and hotel scrapers.
"""

import logging
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


def generate_output_filename(
    prefix: str,
    extension: str,
    output_dir: str = ".",
    timestamp: Optional[datetime] = None,
    location: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
) -> str:
    """
    Generate a standardized output filename.

    Args:
        prefix: Filename prefix (e.g., 'trave_flight_tickets', 'trave_hotel_results').
        extension: File extension (e.g., 'csv', 'json').
        output_dir: Directory to save the file.
        timestamp: Timestamp to include in filename. Uses current time if None.
        location: Location name for hotel searches (optional).
        origin: Origin airport code for flight searches (optional).
        destination: Destination airport code for flight searches (optional).

    Returns:
        Full path to the output file.

    Example:
        ```python
        # Flight search
        generate_output_filename("trave_flight_tickets", "csv", origin="CGK", destination="DPS")
        # Hotel search
        generate_output_filename("trave_hotel_results", "csv", location="Jakarta")
        ```
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Build filename
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
    parts = [prefix]

    # Add location or route information
    if location:
        # Sanitize location name for filename
        safe_location = location.replace(" ", "_").replace("/", "_").lower()
        parts.append(safe_location)
    elif origin and destination:
        parts.append(f"{origin.upper()}_{destination.upper()}")

    parts.append(timestamp_str)

    filename = "_".join(parts) + f".{extension}"
    filepath = os.path.join(output_dir, filename)

    logger.debug(f"Generated output filename: {filepath}")
    return filepath


def save_to_csv(
    data: List[Dict[str, Any]],
    filepath: str,
    include_timestamp: bool = True,
) -> str:
    """
    Save data to CSV file using pandas.

    Args:
        data: List of dictionaries to save.
        filepath: Path to the output CSV file.
        include_timestamp: Whether to add a saved_at column.

    Returns:
        Path to the saved file.
    """
    if not data:
        raise ValueError("No data to save")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

    # Add timestamp if requested
    if include_timestamp:
        timestamp = datetime.now().isoformat()
        for item in data:
            item["saved_at"] = timestamp

    df = pd.DataFrame(data)
    # Use QUOTE_ALL to properly handle newlines and special characters in data
    df.to_csv(filepath, index=False, quoting=csv.QUOTE_ALL, escapechar="\\")

    logger.info(f"Data saved to CSV: {filepath}")
    return filepath


def save_to_json(
    data: Dict[str, Any],
    filepath: str,
    indent: int = 2,
) -> str:
    """
    Save data to JSON file.

    Args:
        data: Dictionary to save.
        filepath: Path to the output JSON file.
        indent: JSON indentation level.

    Returns:
        Path to the saved file.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        logger.info(f"Data saved to JSON: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        raise

    return filepath


def load_from_csv(filepath: str) -> pd.DataFrame:
    """
    Load data from a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pandas DataFrame with the loaded data.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    return pd.read_csv(filepath)


def load_from_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Dictionary with the loaded data.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directory_exists(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory.

    Returns:
        Path to the directory.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory


def parse_price_to_numeric(price_str: str) -> Optional[float]:
    """
    Parse a price string to a numeric value.

    Handles formats like "Rp 1.500.000" or "$1,500.00".

    Args:
        price_str: Price string to parse.

    Returns:
        Numeric price value or None if parsing fails.
    """
    if not price_str:
        return None

    # Remove currency symbols and whitespace
    cleaned = price_str.replace("Rp", "").replace("$", "").replace(",", "").strip()

    # Remove thousand separators (dots in Indonesian format)
    cleaned = cleaned.replace(".", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def format_duration_to_minutes(duration_str: str) -> Optional[int]:
    """
    Parse a duration string to total minutes.

    Handles formats like "2h 30m", "2h", "30m".

    Args:
        duration_str: Duration string to parse.

    Returns:
        Total minutes or None if parsing fails.
    """
    if not duration_str:
        return None

    total_minutes = 0

    # Parse hours
    if "h" in duration_str:
        hours_part = duration_str.split("h")[0].strip()
        try:
            total_minutes += int(hours_part) * 60
        except ValueError:
            return None

    # Parse minutes
    if "m" in duration_str:
        if "h" in duration_str:
            minutes_part = duration_str.split("h")[1].split("m")[0].strip()
        else:
            minutes_part = duration_str.split("m")[0].strip()

        try:
            total_minutes += int(minutes_part)
        except ValueError:
            return None

    return total_minutes if total_minutes > 0 else None


def create_search_summary(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    location: Optional[str] = None,
    num_results: int = 0,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
) -> str:
    """
    Create a human-readable search summary.

    Args:
        origin: Origin airport code (for flights).
        destination: Destination airport code (for flights).
        location: Location name (for hotels).
        num_results: Number of results found.
        min_price: Minimum price (optional).
        max_price: Maximum price (optional).

    Returns:
        Formatted summary string.
    """
    if origin and destination:
        summary = f"Flight search: {origin} → {destination} | Found {num_results} flights"
    elif location:
        summary = f"Hotel search: {location} | Found {num_results} hotels"
    else:
        summary = f"Search complete | Found {num_results} results"

    if min_price and max_price:
        summary += f" | Price range: {min_price} - {max_price}"

    return summary
