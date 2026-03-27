"""
Configuration and utilities for Scraprrr.

This module provides base configuration classes and common utilities.
"""

import csv
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ScraperConfig(BaseModel):
    """
    Base configuration for all scrapers.

    Specific scrapers can extend this with their own settings.
    """

    # Selenium settings
    selenium_remote_url: str = Field(
        default="http://localhost:4444/wd/hub",
        description="URL of the Selenium Grid server",
    )
    page_load_timeout: int = Field(
        default=30,
        description="Timeout for page loads in seconds",
    )
    element_wait_timeout: int = Field(
        default=15,
        description="Timeout for element waits in seconds",
    )

    # Scraping settings
    scroll_enabled: bool = Field(
        default=True,
        description="Whether to scroll to load more results",
    )
    scroll_timeout: int = Field(
        default=60,
        description="Maximum time in seconds to scroll",
    )
    scroll_pause: float = Field(
        default=2.0,
        description="Time to wait between scrolls in seconds",
    )

    # Output settings
    save_csv: bool = Field(
        default=True,
        description="Whether to save results to CSV",
    )
    save_json: bool = Field(
        default=False,
        description="Whether to save results to JSON",
    )
    output_dir: str = Field(
        default=".",
        description="Directory to save output files",
    )


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
        prefix: Filename prefix.
        extension: File extension (e.g., 'csv', 'json').
        output_dir: Directory to save the file.
        timestamp: Timestamp to include. Uses current time if None.
        location: Location name for hotel searches.
        origin: Origin airport code for flight searches.
        destination: Destination airport code for flight searches.

    Returns:
        Full path to the output file.
    """
    if timestamp is None:
        timestamp = datetime.now()

    os.makedirs(output_dir, exist_ok=True)

    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
    parts = [prefix]

    if location:
        safe_location = location.replace(" ", "_").replace("/", "_").lower()
        parts.append(safe_location)
    elif origin and destination:
        parts.append(f"{origin.upper()}_{destination.upper()}")

    parts.append(timestamp_str)

    filename = "_".join(parts) + f".{extension}"
    return os.path.join(output_dir, filename)


def save_to_csv(data: List[Dict[str, Any]], filepath: str) -> str:
    """Save data to CSV file."""
    if not data:
        raise ValueError("No data to save")

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)

    # Add timestamp
    timestamp = datetime.now().isoformat()
    for item in data:
        item["saved_at"] = timestamp

    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, quoting=csv.QUOTE_ALL, escapechar="\\")
    logger.info(f"Data saved to CSV: {filepath}")
    return filepath


def save_to_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> str:
    """Save data to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    logger.info(f"Data saved to JSON: {filepath}")
    return filepath


def ensure_directory_exists(directory: str) -> str:
    """Ensure a directory exists, creating it if necessary."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory


def parse_price_to_numeric(price_str: str) -> Optional[float]:
    """Parse a price string to numeric value."""
    if not price_str:
        return None

    cleaned = price_str.replace("Rp", "").replace("$", "").replace(",", "").strip()
    cleaned = cleaned.replace(".", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def format_duration_to_minutes(duration_str: str) -> Optional[int]:
    """Parse a duration string to total minutes."""
    if not duration_str:
        return None

    total_minutes = 0

    if "h" in duration_str:
        hours_part = duration_str.split("h")[0].strip()
        try:
            total_minutes += int(hours_part) * 60
        except ValueError:
            return None

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
