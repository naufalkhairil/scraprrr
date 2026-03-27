"""
Common utilities and shared components for Traveloka scrapers.

This package provides shared functionality used across flight and hotel scrapers:
- WebDriver management
- File I/O utilities
- Common data processing functions
- Base configuration management
"""

from traveloka_scraper_common.driver import create_driver, quit_driver
from traveloka_scraper_common.utils import (
    ensure_directory_exists,
    format_duration_to_minutes,
    generate_output_filename,
    load_from_csv,
    load_from_json,
    parse_price_to_numeric,
    save_to_csv,
    save_to_json,
)

__all__ = [
    # Driver
    "create_driver",
    "quit_driver",
    # Utils
    "generate_output_filename",
    "save_to_csv",
    "save_to_json",
    "load_from_csv",
    "load_from_json",
    "ensure_directory_exists",
    "parse_price_to_numeric",
    "format_duration_to_minutes",
]
